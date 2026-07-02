"""
Template-based reasoning generation.

Deliberately NOT an LLM call (no network, no GPU, must run in seconds for
thousands of candidates). Every justification is built from the structured
features computed in features.py, so it's fully traceable and never
hallucinates — if a claim appears in the justification, it's because a
feature computation produced that exact value.
"""

from __future__ import annotations

from . import config
from .utils import as_list, safe_get


def generate_justification(candidate: dict, feature_result: dict, jd: dict) -> str:
    """Build a human-readable justification string for one candidate's rank.

    feature_result is the dict produced by features.compute_all_features().
    """
    schema = config.SCHEMA
    parts: list[str] = []

    disq = feature_result["disqualifiers"]
    if disq["disqualified"]:
        reasons = "; ".join(disq["reasons"])
        return f"Disqualified — {reasons}."

    honeypot = feature_result["honeypot"]
    if honeypot["honeypot_score"] >= config.HONEYPOT_CONFIG["honeypot_score_exclude"]:
        return (
            f"Excluded — suspicious profile detected "
            f"(honeypot_score={honeypot['honeypot_score']}, "
            f"signals: {', '.join(honeypot['signals'])})."
        )

    # --- Experience summary ---
    exp = feature_result["production_experience"]
    exp_years = safe_get(candidate, schema["experience_years"], 0)
    parts.append(
        f"{exp_years} yrs experience "
        f"(seniority signal {exp['seniority_component']:.2f}, "
        f"skill overlap {exp['skill_overlap_ratio']:.0%})."
    )

    # --- Skill match detail ---
    required_skills = {
        s.strip().lower() for s in as_list(jd.get(config.JD_SECTIONS["required_skills"]))
    }
    candidate_skills = {
        s.strip().lower() for s in as_list(safe_get(candidate, schema["skills"], []))
    }
    matched = sorted(required_skills & candidate_skills)
    missing = sorted(required_skills - candidate_skills)
    if matched:
        parts.append(f"Matches required skills: {', '.join(matched[:6])}"
                      + (" (+more)" if len(matched) > 6 else "") + ".")
    if missing:
        parts.append(f"Missing: {', '.join(missing[:4])}"
                      + (" (+more)" if len(missing) > 4 else "") + ".")

    # --- Behavioral summary ---
    behavioral = feature_result["behavioral"]
    if behavioral.get("avg_tenure_years") is not None:
        parts.append(
            f"Avg tenure {behavioral['avg_tenure_years']} yrs across "
            f"{behavioral['num_jobs']} roles."
        )
        if behavioral.get("short_stints", 0) > 1:
            parts.append(f"Note: {behavioral['short_stints']} short (<1yr) stints.")
    else:
        parts.append("Employment history unavailable — behavioral score neutral.")

    # --- Honeypot borderline flag (not excluded, but worth noting) ---
    if honeypot["honeypot_score"] >= config.HONEYPOT_CONFIG["honeypot_score_floor"]:
        parts.append(
            f"Caution: profile shows minor irregularities "
            f"(score={honeypot['honeypot_score']}, {', '.join(honeypot['signals'])}) "
            f"— down-weighted accordingly."
        )

    return " ".join(parts)


def generate_flags(feature_result: dict) -> list[str]:
    """Short machine-readable flag list to accompany the justification,
    matching config.SUBMISSION_FIELDS['flags']."""
    flags: list[str] = []
    disq = feature_result["disqualifiers"]
    honeypot = feature_result["honeypot"]

    if disq["disqualified"]:
        flags.append("disqualified")
        for reason in disq["reasons"]:
            flags.append(f"disqualified:{reason.split(':')[0]}")

    if honeypot["honeypot_score"] >= config.HONEYPOT_CONFIG["honeypot_score_exclude"]:
        flags.append("honeypot_excluded")
    elif honeypot["honeypot_score"] >= config.HONEYPOT_CONFIG["honeypot_score_floor"]:
        flags.append("honeypot_suspected")

    return flags