# SkillSync AI — Architecture

## System Overview

SkillSync AI is a two-stage candidate ranking pipeline designed to run
under strict constraints: CPU-only, no network at inference, 5-minute
wall-clock limit, and 16 GB RAM.

## Pipeline Stages

### Stage 1: Precompute (`python -m src.precompute`)

Run once, offline, with network access allowed (for initial model download).

```
candidates.jsonl.gz ──┐
                      ├──▶ precompute.py ──▶ artifacts/
job_description.docx ─┘                       ├── models/all-MiniLM-L6-v2/
                                               ├── embeddings/
                                               │   ├── candidate_embeddings.npy
                                               │   ├── candidate_ids.json
                                               │   └── jd_embedding.npy
                                               └── features/
                                                   ├── feature_table.json
                                                   └── parsed_jd.json
```

### Stage 2: Rank (`python -m src.rank`)

Run under constraints. Loads precomputed artifacts and produces output.

```
artifacts/ ──▶ rank.py ──▶ outputs/
                             ├── predictions.json       (submission format)
                             └── predictions_full.json   (audit format)
```

## Module Dependency Graph

```
config.py ◄─── (all modules read configuration from here)
    │
    ▼
utils.py ◄─── (shared IO, logging, text helpers)
    │
    ├──▶ embedding.py    (sentence-transformers encode/save/load)
    │
    ├──▶ features.py     (structured feature computation)
    │       ├── compute_disqualifiers()
    │       ├── compute_honeypot_score()
    │       ├── compute_production_experience_score()
    │       ├── compute_behavioral_composite()
    │       └── detect_duplicate_resumes()  (batch-level)
    │
    ├──▶ reasoning.py    (template-based justification + flags)
    │
    └──▶ ranking_engine.py
            ├── compute_skill_match_score()
            ├── blend_score()
            └── rank_candidates()   ◄── orchestrates features + reasoning
```

## Scoring Formula

```
final_score = w_sem * semantic_similarity
            + w_skill * skill_match
            + w_prod * production_experience
            + w_behav * behavioral_composite

where:
  w_sem   = 0.40 (cosine similarity, resume ↔ JD embeddings)
  w_skill = 0.25 (set overlap, required skills ∩ candidate skills)
  w_prod  = 0.20 (log-scaled years + seniority + skill overlap blend)
  w_behav = 0.15 (tenure stability, career trajectory)
```

### Gating (pre/post blend)

1. **Disqualified** → score = 0.0, excluded, pinned last
2. **Honeypot excluded** (score ≥ 0.6) → score = 0.0, excluded
3. **Honeypot suspected** (score ≥ 0.15) → `final_score *= 0.3`

## Data Schema

Candidate fields are mapped via `config.SCHEMA` — a single indirection
layer so the entire pipeline can adapt to schema changes by editing one file.

JD sections are mapped via `config.JD_SECTIONS`.
