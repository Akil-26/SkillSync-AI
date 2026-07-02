"""
Feature engineering: structured, explainable features computed per candidate.

Every function here returns plain Python types (bool/float/list/str) so
they're trivially serializable to the feature table and easy to explain
in reasoning.py. Nothing here calls the embedding model — that's kept
separate in embedding.py so structured features can be computed even
before/without embeddings.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from . import config
from .utils import as_list, normalize_text, safe_get


# ==========================================================================
# Disqualifier flags (hard requirements)
# ==========================================================================
def compute_disqualifiers(candidate: dict, jd: dict) -> dict[str, Any]:
    """Check hard requirements. Returns dict with 'disqualified' bool and
    'reasons' list explaining exactly why, so we never silently drop someone.
    """
    reasons: list[str] = []
    cfg = config.DISQUALIFIER_CONFIG
    schema = config.SCHEMA
    jd_sections = config.JD_SECTIONS

    # --- Minimum experience ---
    if cfg["enforce_min_experience"]:
        min_years = jd.get(jd_sections["min_experience_years"])
        candidate_years = safe_get(candidate, schema["experience_years"], 0)
        if min_years is not None and candidate_years is not None:
            if candidate_years < min_years:
                reasons.append(
                    f"min_experience_years: has {candidate_years}, requires {min_years}"
                )

    # --- Required skills overlap ---
    if cfg["enforce_required_skills"]:
        required_skills = {
            normalize_text(s) for s in as_list(jd.get(jd_sections["required_skills"]))
        }
        candidate_skills = {
            normalize_text(s) for s in as_list(safe_get(candidate, schema["skills"], []))
        }
        overlap = required_skills & candidate_skills
        if required_skills and len(overlap) < cfg["min_required_skill_overlap"]:
            missing = required_skills - candidate_skills
            reasons.append(
                f"required_skills: missing {sorted(missing)[:5]}"
                + (" (+more)" if len(missing) > 5 else "")
            )

    # --- Work authorization (off by default; flip in config once confirmed) ---
    if cfg["enforce_work_authorization"]:
        work_auth = safe_get(candidate, schema["work_authorization"])
        if work_auth is False:
            reasons.append("work_authorization: candidate not authorized")

    return {
        "disqualified": len(reasons) > 0,
        "reasons": reasons,
    }


# ==========================================================================
# Honeypot / suspicious-profile detection
# ==========================================================================
def compute_honeypot_score(candidate: dict) -> dict[str, Any]:
    """Heuristic honeypot / fraud-signal detector.

    Returns a score in [0, 1] plus the individual signals that fired, so the
    ranking step can floor/exclude and the reasoning step can explain why.

    Signals (each heuristic, cheap, offline-computable):
      - absurd skill-list length (keyword stuffing)
      - resume text too short to be genuine
      - repeated-token stuffing ratio in resume text
      - disposable/throwaway email domain
      - unrealistic total experience years
      - senior title with ~0 years experience (mismatch)
      - duplicate/templated resume text (exact-match handled at batch level,
        see detect_duplicate_resumes)
    """
    schema = config.SCHEMA
    hp_cfg = config.HONEYPOT_CONFIG
    signals: list[str] = []
    score = 0.0

    skills = as_list(safe_get(candidate, schema["skills"], []))
    if len(skills) > hp_cfg["max_skill_count"]:
        signals.append(f"excessive_skill_count:{len(skills)}")
        score += 0.25

    resume_text = safe_get(candidate, schema["resume_text"], "") or ""
    if len(resume_text.strip()) < hp_cfg["min_resume_length_chars"]:
        signals.append("resume_too_short")
        score += 0.2

    stuffing_ratio = _keyword_stuffing_ratio(resume_text)
    if stuffing_ratio >= hp_cfg["keyword_stuffing_repeat_ratio"]:
        signals.append(f"keyword_stuffing:{stuffing_ratio:.2f}")
        score += 0.25

    email = (safe_get(candidate, schema["email"], "") or "").lower()
    domain = email.split("@")[-1] if "@" in email else ""
    if domain in hp_cfg["disposable_email_domains"]:
        signals.append(f"disposable_email_domain:{domain}")
        score += 0.3

    exp_years = safe_get(candidate, schema["experience_years"], 0) or 0
    if exp_years > hp_cfg["max_reasonable_experience_years"]:
        signals.append(f"unrealistic_experience_years:{exp_years}")
        score += 0.3

    title = normalize_text(safe_get(candidate, schema["current_title"], ""))
    senior_markers = ("senior", "lead", "principal", "staff", "head", "director", "vp")
    if any(m in title for m in senior_markers) and exp_years is not None and exp_years < 1:
        signals.append("senior_title_zero_experience_mismatch")
        score += 0.3

    score = min(score, 1.0)
    return {"honeypot_score": round(score, 3), "signals": signals}


def _keyword_stuffing_ratio(text: str) -> float:
    """Fraction of tokens taken up by the single most common token.
    High ratio ~ repeated keyword spam (e.g. 'python python python ...')."""
    tokens = normalize_text(text).split()
    if len(tokens) < 10:
        return 0.0
    counts = Counter(tokens)
    most_common_count = counts.most_common(1)[0][1]
    return most_common_count / len(tokens)


def detect_duplicate_resumes(candidates: list[dict]) -> dict[str, list[str]]:
    """Batch-level honeypot signal: exact-duplicate resume text across
    different candidate_ids (template farms / bot-generated profiles).

    Returns {candidate_id: [other_candidate_ids_sharing_this_text]} for any
    candidate involved in a duplicate group.
    """
    schema = config.SCHEMA
    text_to_ids: dict[str, list[str]] = {}
    for c in candidates:
        text = normalize_text(safe_get(c, schema["resume_text"], ""))
        cid = safe_get(c, schema["id"], "")
        if not text or not cid:
            continue
        text_to_ids.setdefault(text, []).append(cid)

    duplicates: dict[str, list[str]] = {}
    for ids in text_to_ids.values():
        if len(ids) > 1:
            for cid in ids:
                duplicates[cid] = [other for other in ids if other != cid]
    return duplicates


# ==========================================================================
# Production-experience score
# ==========================================================================
def compute_production_experience_score(candidate: dict, jd: dict) -> dict[str, Any]:
    """Score reflecting hands-on, production-grade experience relevance.

    Blends: years of experience (log-scaled, diminishing returns),
    seniority signal from titles, and overlap between candidate's past
    companies/projects tech stack and JD's required skills.
    """
    schema = config.SCHEMA

    exp_years = safe_get(candidate, schema["experience_years"], 0) or 0
    # Diminishing returns: 0->0, 2->~0.5, 5->~0.75, 10->~0.9 (log curve capped at 1)
    years_component = min(math.log1p(exp_years) / math.log1p(10), 1.0)

    titles = " ".join(as_list(safe_get(candidate, schema["past_titles"], []))).lower()
    titles += " " + normalize_text(safe_get(candidate, schema["current_title"], ""))
    seniority_markers = {
        "intern": 0.1, "junior": 0.3, "associate": 0.4, "engineer": 0.5,
        "senior": 0.75, "lead": 0.85, "staff": 0.9, "principal": 0.95,
        "director": 0.9, "head": 0.9, "vp": 0.95,
    }
    seniority_component = max(
        (score for marker, score in seniority_markers.items() if marker in titles),
        default=0.4,
    )

    required_skills = {
        normalize_text(s) for s in as_list(jd.get(config.JD_SECTIONS["required_skills"]))
    }
    candidate_skills = {
        normalize_text(s) for s in as_list(safe_get(candidate, schema["skills"], []))
    }
    if required_skills:
        skill_overlap_ratio = len(required_skills & candidate_skills) / len(required_skills)
    else:
        skill_overlap_ratio = 0.5  # neutral if JD gives no explicit skill list

    score = (
        0.4 * years_component
        + 0.3 * seniority_component
        + 0.3 * skill_overlap_ratio
    )

    return {
        "production_experience_score": round(score, 3),
        "years_component": round(years_component, 3),
        "seniority_component": round(seniority_component, 3),
        "skill_overlap_ratio": round(skill_overlap_ratio, 3),
    }


# ==========================================================================
# Behavioral composite (tenure stability, growth trajectory)
# ==========================================================================
def compute_behavioral_composite(candidate: dict) -> dict[str, Any]:
    """Score reflecting career stability & growth trajectory from employment
    history. Penalizes extreme job-hopping and unexplained long gaps;
    rewards steady tenure and upward title progression.

    NOTE: employment_history schema is assumed as a list of dicts with
    'start_date', 'end_date' (or None for current), 'title'. Adjust the
    parsing in _parse_employment_history() once the real schema is known.
    """
    schema = config.SCHEMA
    history = as_list(safe_get(candidate, schema["employment_history"], []))

    if not history:
        return {
            "behavioral_composite": 0.5,  # neutral default, not enough signal
            "avg_tenure_years": None,
            "num_jobs": 0,
            "note": "no employment_history available",
        }

    tenures = _parse_employment_history(history)
    if not tenures:
        return {
            "behavioral_composite": 0.5,
            "avg_tenure_years": None,
            "num_jobs": len(history),
            "note": "employment_history present but dates unparseable",
        }

    avg_tenure = sum(tenures) / len(tenures)
    # Reward tenure up to ~3 years, diminishing returns after (avoid penalizing
    # long single-company careers, but don't over-reward either).
    tenure_component = min(avg_tenure / 3.0, 1.0)

    num_jobs = len(tenures)
    # Job-hopping penalty: many very short stints is a negative signal.
    short_stints = sum(1 for t in tenures if t < 1.0)
    hopping_penalty = min(short_stints / max(num_jobs, 1), 1.0) * 0.3

    score = max(0.0, min(1.0, tenure_component - hopping_penalty))

    return {
        "behavioral_composite": round(score, 3),
        "avg_tenure_years": round(avg_tenure, 2),
        "num_jobs": num_jobs,
        "short_stints": short_stints,
    }


def _parse_employment_history(history: list[dict]) -> list[float]:
    """Return list of tenure-in-years floats, skipping unparseable entries."""
    from datetime import date, datetime

    tenures = []
    for job in history:
        if not isinstance(job, dict):
            continue
        start = job.get("start_date")
        end = job.get("end_date")  # None/absent = current job
        if not start:
            continue
        try:
            start_dt = datetime.fromisoformat(str(start)[:10])
            end_dt = datetime.fromisoformat(str(end)[:10]) if end else datetime.combine(
                date.today(), datetime.min.time()
            )
            years = (end_dt - start_dt).days / 365.25
            if years >= 0:
                tenures.append(years)
        except (ValueError, TypeError):
            continue
    return tenures


# ==========================================================================
# Orchestration: compute all structured features for one candidate
# ==========================================================================
def compute_all_features(candidate: dict, jd: dict) -> dict[str, Any]:
    """Compute the full structured feature set for a single candidate."""
    schema = config.SCHEMA
    result: dict[str, Any] = {"candidate_id": safe_get(candidate, schema["id"])}

    result["disqualifiers"] = compute_disqualifiers(candidate, jd)
    result["honeypot"] = compute_honeypot_score(candidate)
    result["production_experience"] = compute_production_experience_score(candidate, jd)
    result["behavioral"] = compute_behavioral_composite(candidate)

    return result