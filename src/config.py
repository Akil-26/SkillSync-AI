"""
Project-wide configuration and constants.

IMPORTANT: This is the ONE file to edit once the real Redrob dataset is
available. Everything else (features.py, embedding.py, ranking_engine.py)
reads field names from SCHEMA below rather than hardcoding them, so pointing
the pipeline at the real data should mostly mean editing this file.

Current field names under SCHEMA are ASSUMPTIONS based on typical
candidate/resume datasets. Replace with the actual keys from
candidates.jsonl.gz as soon as it's available.
"""

from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
CANDIDATES_PATH = DATA_DIR / "candidates.jsonl.gz"
JOB_DESCRIPTION_PATH = DATA_DIR / "job_description.docx"
SAMPLE_DATA_DIR = DATA_DIR / "sample_data"

ARTIFACTS_DIR = ROOT_DIR / "artifacts"
EMBEDDINGS_DIR = ARTIFACTS_DIR / "embeddings"
FEATURES_DIR = ARTIFACTS_DIR / "features"
MODELS_DIR = ARTIFACTS_DIR / "models"

CANDIDATE_EMBEDDINGS_PATH = EMBEDDINGS_DIR / "candidate_embeddings.npy"
CANDIDATE_IDS_PATH = EMBEDDINGS_DIR / "candidate_ids.json"
JD_EMBEDDING_PATH = EMBEDDINGS_DIR / "jd_embedding.npy"
FEATURE_TABLE_PATH = FEATURES_DIR / "feature_table.parquet"

OUTPUTS_DIR = ROOT_DIR / "outputs"
PREDICTIONS_PATH = OUTPUTS_DIR / "predictions.json"
LOGS_DIR = OUTPUTS_DIR / "logs"

# --------------------------------------------------------------------------
# Embedding model
# --------------------------------------------------------------------------
# Must be pre-downloaded into MODELS_DIR during setup (network allowed then).
# The actual ranking run (rank.py) must NOT touch the network, so we load
# from a local cache path, not from the hub, at inference time.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL_LOCAL_PATH = MODELS_DIR / "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
EMBEDDING_BATCH_SIZE = 64

# --------------------------------------------------------------------------
# Schema mapping (ASSUMED — update once real data is inspected)
# --------------------------------------------------------------------------
SCHEMA = {
    "id": "candidate_id",
    "name": "full_name",
    "email": "email",
    "resume_text": "resume_text",          # full free-text resume / summary
    "skills": "skills",                    # list[str]
    "experience_years": "total_experience_years",
    "current_title": "current_title",
    "past_titles": "past_titles",          # list[str]
    "companies": "companies",              # list[str]
    "education": "education",              # list[dict] or list[str]
    "certifications": "certifications",    # list[str]
    "work_authorization": "work_authorization",
    "location": "location",
    "projects": "projects",                # list[dict] with description/tech
    "employment_history": "employment_history",  # list[dict] start/end dates
    "expected_salary": "expected_salary",
    "notice_period_days": "notice_period_days",
}

# Job description parsed sections (assumed headings inside the .docx)
JD_SECTIONS = {
    "title": "title",
    "must_have": "must_have_requirements",   # hard disqualifiers
    "nice_to_have": "nice_to_have",
    "responsibilities": "responsibilities",
    "min_experience_years": "min_experience_years",
    "required_skills": "required_skills",
}

# --------------------------------------------------------------------------
# Ranking weights (blend of embedding similarity + structured features)
# Must sum to 1.0 across the "positive" components; disqualifiers/honeypot
# are applied as separate gating steps, not part of this blend.
# --------------------------------------------------------------------------
SCORE_WEIGHTS = {
    "semantic_similarity": 0.40,   # cosine sim between resume & JD embeddings
    "skill_match": 0.25,           # overlap of required vs candidate skills
    "production_experience": 0.20, # weighted years / seniority signal
    "behavioral_composite": 0.15,  # tenure stability, growth trajectory, etc.
}

# --------------------------------------------------------------------------
# Honeypot detection thresholds
# --------------------------------------------------------------------------
HONEYPOT_CONFIG = {
    "max_skill_count": 60,                 # absurd skill-list length
    "min_resume_length_chars": 80,          # suspiciously thin resume
    "keyword_stuffing_repeat_ratio": 0.35,  # top-token frequency / total tokens
    "max_reasonable_experience_years": 45,
    "disposable_email_domains": {
        "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    },
    "honeypot_score_floor": 0.15,   # if honeypot_score >= this, apply penalty
    "honeypot_score_exclude": 0.6,  # if honeypot_score >= this, exclude entirely
    "honeypot_penalty_multiplier": 0.3,  # down-weight factor for borderline cases
}

# --------------------------------------------------------------------------
# Disqualifier config
# --------------------------------------------------------------------------
DISQUALIFIER_CONFIG = {
    "enforce_min_experience": True,
    "enforce_required_skills": True,
    "min_required_skill_overlap": 1,  # at least N required skills must match
    "enforce_work_authorization": False,  # flip True once JD confirms this matters
}

# --------------------------------------------------------------------------
# Runtime / performance constraints
# --------------------------------------------------------------------------
RUNTIME_CONFIG = {
    "max_ranking_seconds": 300,   # 5-minute hard limit for rank.py
    "max_ram_gb": 16,
    "cpu_only": True,
    "allow_network": False,       # only precompute.py may relax this, once
    "random_seed": 42,
    "top_k_output": None,         # None = rank all candidates
}

# --------------------------------------------------------------------------
# Sample submission format (ASSUMED — replace once sample_data is inspected)
# --------------------------------------------------------------------------
SUBMISSION_FIELDS = {
    "candidate_id": "candidate_id",
    "rank": "rank",
    "score": "score",
    "justification": "justification",
    "flags": "flags",  # e.g. ["honeypot_suspected", "disqualified:min_experience"]
}