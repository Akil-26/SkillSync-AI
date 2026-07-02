"""Tests for src.ranking_engine — score blending, skill matching, full pipeline."""

# pyrefly: ignore [missing-import]
import pytest

# pyrefly: ignore [missing-import]
from src.ranking_engine import blend_score, compute_skill_match_score, rank_candidates
# pyrefly: ignore [missing-import]
from src.features import compute_all_features, detect_duplicate_resumes
# pyrefly: ignore [missing-import]
from src import config


# ==========================================================================
# Skill match score tests
# ==========================================================================
class TestSkillMatchScore:
    def test_perfect_match(self, strong_candidate, jd):
        score = compute_skill_match_score(strong_candidate, jd)
        assert score == 1.0  # C001 has all 6 required skills

    def test_partial_match(self, decent_candidate, jd):
        score = compute_skill_match_score(decent_candidate, jd)
        assert 0.0 < score < 1.0

    def test_no_match(self, jd):
        candidate = {"candidate_id": "X", "skills": ["Cobol", "Fortran"]}
        score = compute_skill_match_score(candidate, jd)
        assert score == 0.0

    def test_no_required_skills_returns_neutral(self):
        jd_no_skills = {"required_skills": []}
        candidate = {"candidate_id": "X", "skills": ["Python"]}
        score = compute_skill_match_score(candidate, jd_no_skills)
        assert score == 0.5  # neutral


# ==========================================================================
# Blend score tests
# ==========================================================================
class TestBlendScore:
    def test_all_ones_gives_one(self):
        score = blend_score(1.0, 1.0, 1.0, 1.0)
        assert abs(score - 1.0) < 1e-6

    def test_all_zeros_gives_zero(self):
        score = blend_score(0.0, 0.0, 0.0, 0.0)
        assert score == 0.0

    def test_weights_sum_to_one(self):
        w = config.SCORE_WEIGHTS
        total = sum(w.values())
        assert abs(total - 1.0) < 1e-6

    def test_semantic_component_dominates(self):
        """Semantic has 40% weight — it should be the largest contributor."""
        score_high_sem = blend_score(1.0, 0.0, 0.0, 0.0)
        score_high_skill = blend_score(0.0, 1.0, 0.0, 0.0)
        assert score_high_sem > score_high_skill


# ==========================================================================
# Full ranking pipeline tests
# ==========================================================================
class TestRankCandidates:
    def _make_semantic_sims(self, candidates):
        """Create mock semantic similarities for testing."""
        sims = {}
        for c in candidates:
            cid = c.get("candidate_id")
            # Simulate: strong candidate gets high sim, others get mid/low
            if cid == "C001":
                sims[cid] = 0.92
            elif cid == "C002":
                sims[cid] = 0.75
            elif cid == "C003":
                sims[cid] = 0.60
            elif cid == "C004":
                sims[cid] = 0.45  # honeypot might have some text similarity
            elif cid == "C005":
                sims[cid] = 0.80
            else:
                sims[cid] = 0.50
        return sims

    def test_returns_all_candidates(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        assert len(results) == len(all_candidates)

    def test_strong_candidate_ranked_first(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        # C001 should be rank 1 (strongest match)
        top = results[0]
        assert top["candidate_id"] == "C001"
        assert top["rank"] == 1
        assert top["score"] > 0.0

    def test_disqualified_candidate_excluded(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        c003 = next(r for r in results if r["candidate_id"] == "C003")
        assert c003["excluded"] is True
        assert c003["score"] == 0.0

    def test_honeypot_candidate_excluded(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        c004 = next(r for r in results if r["candidate_id"] == "C004")
        assert c004["excluded"] is True
        assert c004["score"] == 0.0

    def test_excluded_candidates_pinned_last(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        # Non-excluded should come before excluded
        excluded_ranks = [r["rank"] for r in results if r["excluded"]]
        non_excluded_ranks = [r["rank"] for r in results if not r["excluded"]]
        if excluded_ranks and non_excluded_ranks:
            assert min(excluded_ranks) > max(non_excluded_ranks)

    def test_results_sorted_by_score_desc(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        non_excluded = [r for r in results if not r["excluded"]]
        scores = [r["score"] for r in non_excluded]
        assert scores == sorted(scores, reverse=True)

    def test_each_result_has_required_fields(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        for r in results:
            assert "candidate_id" in r
            assert "score" in r
            assert "rank" in r
            assert "justification" in r
            assert "flags" in r
            assert "components" in r
            assert "excluded" in r

    def test_duplicate_map_augments_honeypot(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        # Create a fake duplicate map for C002
        dup_map = {"C002": ["C999"]}
        results = rank_candidates(all_candidates, jd, sims, duplicate_map=dup_map)
        c002 = next(r for r in results if r["candidate_id"] == "C002")
        # Score should be affected (either excluded or penalized)
        assert c002["components"]["honeypot_score"] > 0.0

    def test_ranks_are_sequential(self, all_candidates, jd):
        sims = self._make_semantic_sims(all_candidates)
        results = rank_candidates(all_candidates, jd, sims)
        ranks = [r["rank"] for r in results]
        assert sorted(ranks) == list(range(1, len(all_candidates) + 1))
