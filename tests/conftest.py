"""Shared test fixtures for all test modules."""

import sys
from pathlib import Path

# pyrefly: ignore [missing-import]
import pytest

# Ensure project root is on sys.path so `from src import ...` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pyrefly: ignore [missing-import]
from data.sample_data.fixtures import SAMPLE_CANDIDATES, SAMPLE_JD


@pytest.fixture
def jd():
    """Parsed job description fixture."""
    return SAMPLE_JD.copy()


@pytest.fixture
def strong_candidate():
    """C001 — strong match, all required skills, 8 yrs experience."""
    return SAMPLE_CANDIDATES[0].copy()


@pytest.fixture
def decent_candidate():
    """C002 — decent match, some skills missing, 6 yrs experience."""
    return SAMPLE_CANDIDATES[1].copy()


@pytest.fixture
def underqualified_candidate():
    """C003 — disqualified, only 2 yrs experience."""
    return SAMPLE_CANDIDATES[2].copy()


@pytest.fixture
def honeypot_candidate():
    """C004 — suspicious profile, keyword stuffing, fake email."""
    return SAMPLE_CANDIDATES[3].copy()


@pytest.fixture
def job_hopper_candidate():
    """C005 — decent skills but excessive job hopping."""
    return SAMPLE_CANDIDATES[4].copy()


@pytest.fixture
def all_candidates():
    """All 5 sample candidates."""
    return [c.copy() for c in SAMPLE_CANDIDATES]
