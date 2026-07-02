"""Tests for src.reasoning — justification and flag generation."""

# pyrefly: ignore [missing-import]
import pytest

# pyrefly: ignore [missing-import]
from src.features import compute_all_features
# pyrefly: ignore [missing-import]
from src.reasoning import generate_flags, generate_justification


# ==========================================================================
# Justification tests
# ==========================================================================
class TestGenerateJustification:
    def test_strong_candidate_justification(self, strong_candidate, jd):
        features = compute_all_features(strong_candidate, jd)
        justification = generate_justification(strong_candidate, features, jd)
        assert isinstance(justification, str)
        assert len(justification) > 20
        # Should mention experience
        assert "yrs experience" in justification
        # Should mention matched skills
        assert "Matches required skills" in justification

    def test_disqualified_justification(self, underqualified_candidate, jd):
        features = compute_all_features(underqualified_candidate, jd)
        justification = generate_justification(underqualified_candidate, features, jd)
        assert "Disqualified" in justification

    def test_honeypot_excluded_justification(self, honeypot_candidate, jd):
        features = compute_all_features(honeypot_candidate, jd)
        justification = generate_justification(honeypot_candidate, features, jd)
        assert "Excluded" in justification or "suspicious" in justification.lower()

    def test_justification_mentions_missing_skills(self, decent_candidate, jd):
        features = compute_all_features(decent_candidate, jd)
        justification = generate_justification(decent_candidate, features, jd)
        # C002 is missing Django and PostgreSQL
        assert "Missing" in justification

    def test_job_hopper_mentions_tenure(self, job_hopper_candidate, jd):
        features = compute_all_features(job_hopper_candidate, jd)
        justification = generate_justification(job_hopper_candidate, features, jd)
        assert "tenure" in justification.lower() or "roles" in justification.lower()


# ==========================================================================
# Flag generation tests
# ==========================================================================
class TestGenerateFlags:
    def test_strong_candidate_no_flags(self, strong_candidate, jd):
        features = compute_all_features(strong_candidate, jd)
        flags = generate_flags(features)
        assert flags == []

    def test_disqualified_candidate_has_flags(self, underqualified_candidate, jd):
        features = compute_all_features(underqualified_candidate, jd)
        flags = generate_flags(features)
        assert "disqualified" in flags

    def test_honeypot_candidate_has_flags(self, honeypot_candidate, jd):
        features = compute_all_features(honeypot_candidate, jd)
        flags = generate_flags(features)
        assert any("honeypot" in f for f in flags)

    def test_flags_are_strings(self, strong_candidate, jd):
        features = compute_all_features(strong_candidate, jd)
        flags = generate_flags(features)
        assert all(isinstance(f, str) for f in flags)

    def test_disqualified_flags_include_reason(self, underqualified_candidate, jd):
        features = compute_all_features(underqualified_candidate, jd)
        flags = generate_flags(features)
        # Should have specific reason flags like 'disqualified:min_experience_years'
        reason_flags = [f for f in flags if f.startswith("disqualified:")]
        assert len(reason_flags) >= 1
