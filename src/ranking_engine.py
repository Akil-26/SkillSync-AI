"""
Ranking engine: blends semantic similarity + structured features into a
final score, applies disqualifier and honeypot gating, and produces the
sorted, justified candidate list.

Pipeline for one candidate:
  1. If disqualified (hard requirement failure) -> excluded, rank pinned last.
  2. If honeypot_score >= exclude threshold -> excluded, rank pinned last.
  3. Otherwise: blended_score = weighted sum of
       semantic_similarity, skill_match, production_experience, behavioral
     then if honeypot_score >= floor threshold, multiply by penalty factor.
  4. Sort descending by final score.
"""

from __future__ import annotations

from typing import Any

from . import config, features, reasoning
from .utils import as_list, get_logger, safe_get

logger = get_logger(__name__)


def compute_skill_match_score(candidate: dict, jd: dict) -> float:
    schema = config.SCHEMA
    required = {
        s.strip().lower() for s in as_list(jd.get(config.JD_SECTIONS["required_skills"]))
    }
    candidate_skills = {
        s.strip().lower() for s in as_list(safe_get(candidate, schema["skills"], []))
    }
    if not required:
        return 0.5  # neutral if JD lists no explicit required skills
    return len(required & candidate_skills) / len(required)


def blend_score(
    semantic_similarity: float,
    skill_match: float,
    production_experience: float,
    behavioral_composite: float,
) -> float:
    w = config.SCORE_WEIGHTS
    return (
        w["semantic_similarity"] * semantic_similarity
        + w["skill_match"] * skill_match
        + w["production_experience"] * production_experience
        + w["behavioral_composite"] * behavioral_composite
    )


def rank_candidates(
    candidates: list[dict],
    jd: dict,
    semantic_similarities: dict[str, float],
    duplicate_map: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """Run the full ranking pipeline.

    Args:
        candidates: list of raw candidate dicts.
        jd: parsed job description dict (see config.JD_SECTIONS).
        semantic_similarities: {candidate_id: cosine_similarity_to_jd} —
            precomputed via embedding.py.
        duplicate_map: output of features.detect_duplicate_resumes(), used
            to add an extra honeypot signal for template-farm candidates.

    Returns:
        List of result dicts sorted best-first, each containing
        candidate_id, score, justification, flags, and full feature
        breakdown (for debugging / audit — the final submission writer in
        rank.py can subset this to config.SUBMISSION_FIELDS).
    """
    schema = config.SCHEMA
    hp_cfg = config.HONEYPOT_CONFIG
    duplicate_map = duplicate_map or {}

    results: list[dict[str, Any]] = []

    for candidate in candidates:
        cid = safe_get(candidate, schema["id"])
        feat = features.compute_all_features(candidate, jd)

        # augment honeypot with duplicate-resume signal (batch-level)
        if cid in duplicate_map:
            feat["honeypot"]["signals"].append(
                f"duplicate_resume_of:{duplicate_map[cid][:3]}"
            )
            feat["honeypot"]["honeypot_score"] = min(
                1.0, feat["honeypot"]["honeypot_score"] + 0.3
            )

        disqualified = feat["disqualifiers"]["disqualified"]
        honeypot_score = feat["honeypot"]["honeypot_score"]
        excluded = honeypot_score >= hp_cfg["honeypot_score_exclude"]

        semantic_sim = semantic_similarities.get(cid, 0.0)
        skill_match = compute_skill_match_score(candidate, jd)
        prod_exp = feat["production_experience"]["production_experience_score"]
        behavioral = feat["behavioral"]["behavioral_composite"]

        if disqualified or excluded:
            final_score = 0.0
        else:
            final_score = blend_score(semantic_sim, skill_match, prod_exp, behavioral)
            if honeypot_score >= hp_cfg["honeypot_score_floor"]:
                final_score *= hp_cfg["honeypot_penalty_multiplier"]

        justification = reasoning.generate_justification(candidate, feat, jd)
        flags = reasoning.generate_flags(feat)

        results.append({
            "candidate_id": cid,
            "score": round(final_score, 4),
            "excluded": disqualified or excluded,
            "justification": justification,
            "flags": flags,
            "components": {
                "semantic_similarity": round(semantic_sim, 4),
                "skill_match": round(skill_match, 4),
                "production_experience": round(prod_exp, 4),
                "behavioral_composite": round(behavioral, 4),
                "honeypot_score": honeypot_score,
            },
        })

    # Sort: non-excluded first by score desc, excluded candidates pinned last
    results.sort(key=lambda r: (r["excluded"], -r["score"]))

    for i, r in enumerate(results, start=1):
        r["rank"] = i

    n_excluded = sum(1 for r in results if r["excluded"])
    logger.info(f"Ranked {len(results)} candidates ({n_excluded} excluded/disqualified).")

    return results