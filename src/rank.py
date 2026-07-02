# pyrefly: ignore [missing-import]
"""
Stage 2: Offline ranking (the timed, no-network, CPU-only run).

Loads all precomputed artifacts produced by precompute.py and runs the
ranking pipeline to produce the final predictions.json output.

Constraints enforced:
  - No network access (everything read from local artifacts/)
  - CPU-only computation
  - 5-minute hard wall-clock limit (configurable in config.RUNTIME_CONFIG)

Usage:
    python -m src.rank
    python -m src.rank --top-k 20
    python -m src.rank --output results/my_predictions.json
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

# pyrefly: ignore [missing-import]
import numpy as np

from . import config, embedding, ranking_engine
from .utils import (
    get_logger,
    read_json,
    read_jsonl_gz,
    safe_get,
    timer,
    write_json,
)

logger = get_logger("rank", log_file=config.LOGS_DIR / "rank.log")


# -------------------------------------------------------------------------
# Timeout enforcement
# -------------------------------------------------------------------------
class RankingTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise RankingTimeout("Ranking exceeded the maximum allowed time.")


def _enforce_timeout(max_seconds: int) -> None:
    """Set a wall-clock alarm. Works on Unix; on Windows we fall back to
    a manual check in the main loop (signal.SIGALRM unavailable)."""
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(max_seconds)
    # On Windows we track start_time manually (see run())


# -------------------------------------------------------------------------
# Artifact loading
# -------------------------------------------------------------------------
def load_artifacts() -> tuple[list[dict], dict, np.ndarray, list[str], np.ndarray]:
    """Load all precomputed artifacts. Raises clear errors if anything is
    missing so the user knows to run precompute.py first."""

    # Candidates
    if not config.CANDIDATES_PATH.exists():
        raise FileNotFoundError(
            f"Candidates file not found at {config.CANDIDATES_PATH}. "
            f"Place candidates.jsonl.gz in the data/ directory."
        )
    candidates = read_jsonl_gz(config.CANDIDATES_PATH)
    logger.info(f"Loaded {len(candidates)} candidates.")

    # Parsed JD
    jd_path = config.FEATURES_DIR / "parsed_jd.json"
    if not jd_path.exists():
        raise FileNotFoundError(
            f"Parsed JD not found at {jd_path}. Run `python -m src.precompute` first."
        )
    jd = read_json(jd_path)
    logger.info(f"Loaded parsed JD: title={jd.get('title', '?')!r}")

    # Candidate embeddings
    if not config.CANDIDATE_EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Candidate embeddings not found at {config.CANDIDATE_EMBEDDINGS_PATH}. "
            f"Run `python -m src.precompute` first."
        )
    candidate_embeddings, candidate_ids = embedding.load_embeddings(
        config.CANDIDATE_EMBEDDINGS_PATH, config.CANDIDATE_IDS_PATH
    )
    logger.info(
        f"Loaded candidate embeddings: shape={candidate_embeddings.shape}"
    )

    # JD embedding
    if not config.JD_EMBEDDING_PATH.exists():
        raise FileNotFoundError(
            f"JD embedding not found at {config.JD_EMBEDDING_PATH}. "
            f"Run `python -m src.precompute` first."
        )
    jd_embedding = np.load(config.JD_EMBEDDING_PATH)
    logger.info(f"Loaded JD embedding: shape={jd_embedding.shape}")

    return candidates, jd, candidate_embeddings, candidate_ids, jd_embedding


# -------------------------------------------------------------------------
# Output formatting
# -------------------------------------------------------------------------
def format_predictions(
    ranked: list[dict], top_k: int | None = None
) -> list[dict]:
    """Subset the full ranking results to the submission schema defined in
    config.SUBMISSION_FIELDS, optionally limited to top_k results."""
    sf = config.SUBMISSION_FIELDS
    output = []
    for r in ranked:
        if r.get("excluded"):
            continue
        output.append({
            sf["candidate_id"]: r["candidate_id"],
            sf["rank"]: r["rank"],
            sf["score"]: r["score"],
            sf["justification"]: r["justification"],
            sf["flags"]: r["flags"],
        })
    if top_k is not None:
        output = output[:top_k]
    return output


# -------------------------------------------------------------------------
# Main pipeline
# -------------------------------------------------------------------------
def run(top_k: int | None = None, output_path: str | None = None) -> None:
    """Execute the full Stage 2 ranking pipeline."""
    max_seconds = config.RUNTIME_CONFIG["max_ranking_seconds"]
    start_time = time.perf_counter()

    logger.info("=== Stage 2: Ranking starting ===")
    logger.info(f"Time limit: {max_seconds}s | top_k: {top_k or 'all'}")

    _enforce_timeout(max_seconds)

    try:
        # 1. Load all precomputed artifacts
        with timer("load_artifacts", logger):
            candidates, jd, candidate_embeddings, candidate_ids, jd_embedding = (
                load_artifacts()
            )

        # Windows timeout check
        elapsed = time.perf_counter() - start_time
        if elapsed > max_seconds:
            raise RankingTimeout(f"Exceeded {max_seconds}s during artifact loading.")

        # 2. Compute semantic similarities (dot product = cosine sim for
        #    L2-normalised embeddings)
        with timer("compute_similarities", logger):
            similarities = embedding.cosine_similarity_matrix(
                candidate_embeddings, jd_embedding
            )
            semantic_similarities = {
                cid: float(sim) for cid, sim in zip(candidate_ids, similarities)
            }
        logger.info(
            f"Computed similarities for {len(semantic_similarities)} candidates."
        )

        # Windows timeout check
        elapsed = time.perf_counter() - start_time
        if elapsed > max_seconds:
            raise RankingTimeout(f"Exceeded {max_seconds}s during similarity computation.")

        # 3. Detect duplicate resumes (batch-level honeypot signal)
        with timer("detect_duplicates", logger):
            from . import features
            duplicate_map = features.detect_duplicate_resumes(candidates)
        if duplicate_map:
            logger.warning(
                f"Detected {len(duplicate_map)} candidates with duplicate resumes."
            )

        # 4. Run the ranking engine
        with timer("rank_candidates", logger):
            ranked = ranking_engine.rank_candidates(
                candidates, jd, semantic_similarities, duplicate_map
            )

        # Windows timeout check
        elapsed = time.perf_counter() - start_time
        if elapsed > max_seconds:
            raise RankingTimeout(f"Exceeded {max_seconds}s during ranking.")

        # 5. Format and write predictions
        top_k_val = top_k or config.RUNTIME_CONFIG.get("top_k_output")
        predictions = format_predictions(ranked, top_k=top_k_val)

        out_path = config.Path(output_path) if output_path else config.PREDICTIONS_PATH
        write_json(out_path, predictions)

        # Write XLSX for submission/upload
        try:
            import pandas as pd
            xlsx_path = out_path.with_suffix(".xlsx")
            df_records = []
            for p in predictions:
                rec = p.copy()
                if isinstance(rec.get("flags"), list):
                    rec["flags"] = ", ".join(rec["flags"])
                df_records.append(rec)
            df = pd.DataFrame(df_records)
            df.to_excel(xlsx_path, index=False)
            logger.info(f"Wrote Excel predictions to {xlsx_path}")
        except Exception as ex:
            logger.error(f"Failed to write Excel output: {ex}")

        # Also write the full ranked list (with component scores) for audit
        full_output_path = out_path.parent / "predictions_full.json"
        write_json(full_output_path, ranked)

        elapsed = time.perf_counter() - start_time
        logger.info(f"=== Stage 2: Ranking complete in {elapsed:.2f}s ===")
        logger.info(
            f"Wrote {len(predictions)} predictions to {out_path}"
        )
        logger.info(f"Full audit output at {full_output_path}")

        # Print summary to stdout
        print(f"\n{'='*60}")
        print(f"  SkillSync AI — Ranking Complete")
        print(f"{'='*60}")
        print(f"  Candidates processed : {len(candidates)}")
        print(f"  Ranked (non-excluded): {len(predictions)}")
        print(f"  Excluded/disqualified: {len(candidates) - len(predictions)}")
        print(f"  Wall-clock time      : {elapsed:.2f}s")
        print(f"  Output               : {out_path}")
        print(f"{'='*60}")

        if predictions:
            print(f"\n  Top 5 candidates:")
            for p in predictions[:5]:
                print(
                    f"    #{p[config.SUBMISSION_FIELDS['rank']]:>3}  "
                    f"score={p[config.SUBMISSION_FIELDS['score']]:.4f}  "
                    f"id={p[config.SUBMISSION_FIELDS['candidate_id']]}"
                )
            print()

    except RankingTimeout as e:
        logger.error(str(e))
        print(f"\n❌ TIMEOUT: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Cancel any pending alarm
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SkillSync AI — Stage 2: Rank candidates (offline, no-network).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Only output the top K candidates (default: all non-excluded).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Path for the predictions JSON (default: {config.PREDICTIONS_PATH}).",
    )
    args = parser.parse_args()
    run(top_k=args.top_k, output_path=args.output)


if __name__ == "__main__":
    main()
