"""Tests for src.features — disqualifiers, honeypot, experience, behavioral."""

# pyrefly: ignore [missing-import]
import pytest

# pyrefly: ignore [missing-import]
from src.features import (
    compute_all_features,
    compute_behavioral_composite,
    compute_disqualifiers,
    compute_honeypot_score,
    compute_production_experience_score,
    detect_duplicate_resumes,
)


# ==========================================================================
# Disqualifier tests
# ==========================================================================
class TestDisqualifiers:
    def test_strong_candidate_not_disqualified(self, strong_candidate, jd):
        result = compute_disqualifiers(strong_candidate, jd)
        assert result["disqualified"] is False
        assert result["reasons"] == []

    def test_underqualified_candidate_disqualified(self, underqualified_candidate, jd):
        result = compute_disqualifiers(underqualified_candidate, jd)
        assert result["disqualified"] is True
        assert len(result["reasons"]) >= 1
        assert any("min_experience_years" in r for r in result["reasons"])

    def test_decent_candidate_not_disqualified(self, decent_candidate, jd):
        """C002 has 6 years experience — above the 5 year minimum."""
        result = compute_disqualifiers(decent_candidate, jd)
        assert result["disqualified"] is False

    def test_no_skills_overlap_disqualifies(self, jd):
        """Candidate with zero overlap on required skills should be disqualified."""
        candidate = {
            "candidate_id": "TEST",
            "skills": ["Haskell", "Erlang", "Prolog"],
            "total_experience_years": 10,
        }
        result = compute_disqualifiers(candidate, jd)
        assert result["disqualified"] is True
        assert any("required_skills" in r for r in result["reasons"])

    def test_one_skill_overlap_passes(self, jd):
        """At least 1 required skill overlap should pass (min_required_skill_overlap=1)."""
        candidate = {
            "candidate_id": "TEST",
            "skills": ["Python"],
            "total_experience_years": 10,
        }
        result = compute_disqualifiers(candidate, jd)
        assert result["disqualified"] is False


# ==========================================================================
# Honeypot detection tests
# ==========================================================================
class TestHoneypot:
    def test_normal_candidate_low_score(self, strong_candidate):
        result = compute_honeypot_score(strong_candidate)
        assert result["honeypot_score"] < 0.15
        assert result["signals"] == []

    def test_suspicious_candidate_high_score(self, honeypot_candidate):
        result = compute_honeypot_score(honeypot_candidate)
        assert result["honeypot_score"] >= 0.6  # should be excluded
        assert len(result["signals"]) >= 2

    def test_disposable_email_flagged(self):
        candidate = {
            "candidate_id": "TEST",
            "email": "test@mailinator.com",
            "skills": ["Python"],
            "resume_text": "A normal resume with enough text to not be flagged as too short. " * 5,
            "total_experience_years": 5,
            "current_title": "Engineer",
        }
        result = compute_honeypot_score(candidate)
        assert any("disposable_email" in s for s in result["signals"])

    def test_excessive_skills_flagged(self):
        candidate = {
            "candidate_id": "TEST",
            "email": "test@gmail.com",
            "skills": [f"skill_{i}" for i in range(70)],
            "resume_text": "A normal resume with enough text. " * 10,
            "total_experience_years": 5,
            "current_title": "Engineer",
        }
        result = compute_honeypot_score(candidate)
        assert any("excessive_skill_count" in s for s in result["signals"])

    def test_senior_title_zero_experience(self):
        candidate = {
            "candidate_id": "TEST",
            "email": "test@gmail.com",
            "skills": ["Python"],
            "resume_text": "A decent resume. " * 10,
            "total_experience_years": 0,
            "current_title": "Senior Staff Director",
        }
        result = compute_honeypot_score(candidate)
        assert any("senior_title_zero_experience" in s for s in result["signals"])


# ==========================================================================
# Production experience tests
# ==========================================================================
class TestProductionExperience:
    def test_experienced_candidate_scores_high(self, strong_candidate, jd):
        result = compute_production_experience_score(strong_candidate, jd)
        assert result["production_experience_score"] > 0.7

    def test_junior_candidate_scores_lower(self, underqualified_candidate, jd):
        result = compute_production_experience_score(underqualified_candidate, jd)
        assert result["production_experience_score"] < 0.6

    def test_score_is_bounded(self, strong_candidate, jd):
        result = compute_production_experience_score(strong_candidate, jd)
        assert 0.0 <= result["production_experience_score"] <= 1.0

    def test_zero_experience(self, jd):
        candidate = {
            "candidate_id": "TEST",
            "total_experience_years": 0,
            "skills": [],
            "current_title": "",
            "past_titles": [],
        }
        result = compute_production_experience_score(candidate, jd)
        assert result["years_component"] == 0.0


# ==========================================================================
# Behavioral composite tests
# ==========================================================================
class TestBehavioralComposite:
    def test_stable_candidate_scores_well(self, strong_candidate):
        result = compute_behavioral_composite(strong_candidate)
        assert result["behavioral_composite"] > 0.5
        assert result["num_jobs"] == 3

    def test_job_hopper_penalized(self, job_hopper_candidate):
        result = compute_behavioral_composite(job_hopper_candidate)
        # Job hopper should have lower score due to many short stints
        assert result["short_stints"] >= 3
        assert result["behavioral_composite"] < 0.7

    def test_no_history_returns_neutral(self):
        candidate = {
            "candidate_id": "TEST",
            "employment_history": [],
        }
        result = compute_behavioral_composite(candidate)
        assert result["behavioral_composite"] == 0.5
        assert result["note"] == "no employment_history available"

    def test_score_is_bounded(self, strong_candidate):
        result = compute_behavioral_composite(strong_candidate)
        assert 0.0 <= result["behavioral_composite"] <= 1.0


# ==========================================================================
# Duplicate detection tests
# ==========================================================================
class TestDuplicateDetection:
    def test_no_duplicates_in_normal_data(self, all_candidates):
        result = detect_duplicate_resumes(all_candidates)
        assert result == {}

    def test_detects_exact_duplicates(self):
        candidates = [
            {"candidate_id": "A", "resume_text": "Same resume text here"},
            {"candidate_id": "B", "resume_text": "Same resume text here"},
            {"candidate_id": "C", "resume_text": "Different resume text"},
        ]
        result = detect_duplicate_resumes(candidates)
        assert "A" in result
        assert "B" in result
        assert "C" not in result
        assert result["A"] == ["B"]
        assert result["B"] == ["A"]


# ==========================================================================
# Integration: compute_all_features
# ==========================================================================
class TestComputeAllFeatures:
    def test_returns_all_components(self, strong_candidate, jd):
        result = compute_all_features(strong_candidate, jd)
        assert "candidate_id" in result
        assert "disqualifiers" in result
        assert "honeypot" in result
        assert "production_experience" in result
        assert "behavioral" in result

    def test_candidate_id_propagated(self, strong_candidate, jd):
        result = compute_all_features(strong_candidate, jd)
        assert result["candidate_id"] == "C001"
