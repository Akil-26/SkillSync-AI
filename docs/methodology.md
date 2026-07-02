# SkillSync AI — Methodology

## Problem Statement

Given a set of candidate profiles (resumes) and a single job description,
rank all candidates by fit quality, producing a justified, explainable
ranking with fraud/honeypot detection.

## Approach: Hybrid Semantic + Structured Ranking

We deliberately avoid a pure LLM-based approach for ranking because:
1. **Reproducibility** — Template-based reasoning produces identical output for identical input
2. **Speed** — Must rank thousands of candidates in under 5 minutes on CPU
3. **Explainability** — Every score component is traceable to a specific feature
4. **No hallucination** — Justifications reference computed values, not generated text

### Semantic Component (40% weight)

- **Model**: `all-MiniLM-L6-v2` (384-dim, CPU-friendly, ~22M params)
- **Why this model**: Best accuracy/speed tradeoff for CPU-only constraint.
  Larger models (e.g., `all-mpnet-base-v2`) offer marginal accuracy gains
  but 3× slower encoding.
- **Method**: Encode each candidate's resume text + titles + skills into a
  single embedding. Cosine similarity against the JD embedding.
- **Normalization**: L2-normalized at encode time so dot product = cosine sim.

### Skill Match Component (25% weight)

- **Method**: Set intersection of required skills (from JD) vs. candidate skills
- **Score**: `|required ∩ candidate| / |required|`
- **Why separate from semantic**: Semantic similarity can miss exact skill
  names when they appear in different phrasings. Explicit set matching
  catches direct hits that embedding similarity might score loosely.

### Production Experience Component (20% weight)

Three sub-signals blended 40/30/30:
1. **Years** — `log(1 + years) / log(11)` → diminishing returns (2 yrs ≈ 0.5, 5 yrs ≈ 0.75, 10 yrs ≈ 0.9)
2. **Seniority** — Keyword matching on current + past titles (intern=0.1 → principal=0.95)
3. **Skill overlap ratio** — Same as skill match, used here to weight experience relevance

### Behavioral Composite Component (15% weight)

Computed from employment history:
- **Average tenure** — Reward up to ~3 years (capped at 1.0)
- **Job-hopping penalty** — Fraction of stints < 1 year × 0.3 penalty
- **Neutral default** — 0.5 when employment history is unavailable

## Honeypot / Fraud Detection

Heuristic signals (no ML model needed):

| Signal | Weight | Threshold |
|---|---|---|
| Excessive skill count | +0.25 | > 60 skills |
| Resume too short | +0.20 | < 80 chars |
| Keyword stuffing ratio | +0.25 | Top token > 35% of all tokens |
| Disposable email domain | +0.30 | Known throwaway domains |
| Unrealistic experience | +0.30 | > 45 years |
| Senior title + 0 years exp | +0.30 | Mismatch detection |
| Duplicate resume text | +0.30 | Exact match across candidates |

Scores are additive, capped at 1.0:
- **≥ 0.15**: Score penalized (multiplied by 0.3)
- **≥ 0.60**: Candidate excluded entirely

## Disqualifier Logic

Hard gates applied before scoring:
1. **Minimum experience years** — Candidate years < JD minimum
2. **Required skills overlap** — Must match ≥ 1 required skill
3. **Work authorization** — Configurable (off by default)

Disqualified candidates receive score = 0.0 and are pinned to the bottom
of the ranking with explicit reasons in their justification.

## Justification Generation

Template-based, not LLM-generated. Each justification includes:
- Experience summary (years, seniority signal, skill overlap %)
- Matched and missing required skills
- Behavioral summary (average tenure, number of roles, short stints)
- Honeypot warnings for borderline cases

This ensures:
- **Zero hallucination risk**
- **Full traceability** to computed features
- **Consistent format** across all candidates
- **Sub-millisecond generation** per candidate
