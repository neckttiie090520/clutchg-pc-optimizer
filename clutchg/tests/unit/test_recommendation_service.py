"""
Unit tests for core.recommendation_service — the single authoritative
recommendation engine.

Covers:
  1. Complete high-end desktop -> primary path used
  2. Mid-range desktop with enough data -> primary path used
  3. Laptop with insufficient data -> fallback path used
  4. Missing RAM / missing score / incomplete profile -> fallback path used
  5. Fallback never recommends EXTREME
  6. Dashboard and scripts consume the same recommendation for the same profile
  7. None profile -> safe fallback
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap (mirrors the other unit tests in this directory)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.recommendation_service import (
    Recommendation,
    recommend_preset,
    _has_sufficient_data,
    _primary_recommendation,
    _fallback_recommendation,
)


# ---------------------------------------------------------------------------
# Lightweight stand-ins for SystemProfile and its nested dataclasses so
# tests stay isolated from system_info.py hardware detection.
# ---------------------------------------------------------------------------


@dataclass
class _FakeRAM:
    total_gb: int
    type: str = "ddr4"
    speed: int = 3200
    score: int = 15


@dataclass
class _FakeOS:
    platform: str = "windows"
    version: str = "10.0.22621"
    build: str = "22621"
    architecture: str = "x64"


@dataclass
class _FakeCPU:
    name: str = "Test CPU"
    vendor: str = "intel"
    cores: int = 8
    threads: int = 16
    base_clock: float = 3.6
    score: int = 25
    benchmark_matched: bool = True


@dataclass
class _FakeGPU:
    name: str = "Test GPU"
    vendor: str = "nvidia"
    vram: int = 8
    driver_version: str = "555.0"
    score: int = 25
    benchmark_matched: bool = True


@dataclass
class _FakeStorage:
    primary_type: str = "nvme"
    total_gb: int = 512
    score: int = 10


@dataclass
class _FakeProfile:
    """Minimal stand-in for SystemProfile."""

    os: _FakeOS
    cpu: _FakeCPU
    gpu: _FakeGPU
    ram: _FakeRAM
    storage: _FakeStorage
    form_factor: str
    tier: str
    total_score: int


def _make_profile(
    total_score: int = 60,
    form_factor: str = "desktop",
    tier: str = "high",
    ram_gb: int = 16,
    cpu_matched: bool = True,
    gpu_matched: bool = True,
) -> _FakeProfile:
    """Helper to build a fake profile with sane defaults."""
    return _FakeProfile(
        os=_FakeOS(),
        cpu=_FakeCPU(benchmark_matched=cpu_matched),
        gpu=_FakeGPU(benchmark_matched=gpu_matched),
        ram=_FakeRAM(total_gb=ram_gb),
        storage=_FakeStorage(),
        form_factor=form_factor,
        tier=tier,
        total_score=total_score,
    )


# ===========================================================================
# Data sufficiency checks
# ===========================================================================


@pytest.mark.unit
class TestDataSufficiency:
    """Tests for _has_sufficient_data()."""

    def test_complete_profile_is_sufficient(self):
        p = _make_profile(total_score=70, form_factor="desktop", ram_gb=16)
        assert _has_sufficient_data(p) is True

    def test_unknown_form_factor_is_insufficient(self):
        p = _make_profile(form_factor="unknown")
        assert _has_sufficient_data(p) is False

    def test_missing_score_is_insufficient(self):
        p = _make_profile()
        p.total_score = None  # type: ignore[assignment]
        assert _has_sufficient_data(p) is False

    def test_zero_ram_is_insufficient(self):
        p = _make_profile(ram_gb=0)
        assert _has_sufficient_data(p) is False

    def test_no_ram_attr_is_insufficient(self):
        """Profile with ram=None should be caught."""
        p = _make_profile()
        p.ram = None  # type: ignore[assignment]
        assert _has_sufficient_data(p) is False

    def test_none_profile_is_insufficient(self):
        assert _has_sufficient_data(None) is False


# ===========================================================================
# Primary (score-based) path
# ===========================================================================


@pytest.mark.unit
class TestPrimaryRecommendation:
    """Tests for the score-based primary path."""

    def test_high_end_desktop_gets_extreme(self):
        p = _make_profile(total_score=85, form_factor="desktop", ram_gb=32)
        rec = _primary_recommendation(p)
        assert rec.preset == "extreme"
        assert rec.source == "primary"

    def test_mid_range_desktop_gets_competitive(self):
        p = _make_profile(total_score=55, form_factor="desktop", ram_gb=16)
        rec = _primary_recommendation(p)
        assert rec.preset == "competitive"
        assert rec.source == "primary"

    def test_low_score_gets_safe(self):
        p = _make_profile(total_score=30, form_factor="desktop", ram_gb=4)
        rec = _primary_recommendation(p)
        assert rec.preset == "safe"
        assert rec.source == "primary"

    def test_high_score_laptop_gets_competitive_not_extreme(self):
        """Laptop with high score: EXTREME requires desktop form factor."""
        p = _make_profile(total_score=90, form_factor="laptop", ram_gb=32)
        rec = _primary_recommendation(p)
        # score >= 80 but not desktop, so falls to competitive check
        assert rec.preset == "competitive"
        assert rec.source == "primary"

    def test_score_boundary_80_desktop_16gb_gets_extreme(self):
        p = _make_profile(total_score=80, form_factor="desktop", ram_gb=16)
        rec = _primary_recommendation(p)
        assert rec.preset == "extreme"

    def test_score_boundary_50_8gb_gets_competitive(self):
        p = _make_profile(total_score=50, form_factor="desktop", ram_gb=8)
        rec = _primary_recommendation(p)
        assert rec.preset == "competitive"

    def test_score_49_gets_safe(self):
        p = _make_profile(total_score=49, form_factor="desktop", ram_gb=8)
        rec = _primary_recommendation(p)
        assert rec.preset == "safe"

    def test_total_score_included_in_result(self):
        p = _make_profile(total_score=72)
        rec = _primary_recommendation(p)
        assert rec.total_score == 72


# ===========================================================================
# Fallback (conservative heuristic) path
# ===========================================================================


@pytest.mark.unit
class TestFallbackRecommendation:
    """Tests for the conservative fallback path."""

    def test_laptop_always_safe(self):
        p = _make_profile(form_factor="laptop", tier="enthusiast")
        rec = _fallback_recommendation(p)
        assert rec.preset == "safe"
        assert rec.source == "fallback"

    def test_desktop_high_tier_gets_competitive(self):
        p = _make_profile(form_factor="desktop", tier="high")
        rec = _fallback_recommendation(p)
        assert rec.preset == "competitive"
        assert rec.source == "fallback"

    def test_desktop_entry_tier_gets_safe(self):
        p = _make_profile(form_factor="desktop", tier="entry")
        rec = _fallback_recommendation(p)
        assert rec.preset == "safe"
        assert rec.source == "fallback"

    def test_unknown_form_factor_entry_gets_safe(self):
        p = _make_profile(form_factor="unknown", tier="entry")
        rec = _fallback_recommendation(p)
        assert rec.preset == "safe"
        assert rec.source == "fallback"

    def test_fallback_never_returns_extreme(self):
        """Core invariant: fallback should NEVER recommend extreme."""
        for ff in ("desktop", "laptop", "unknown"):
            for tier in ("entry", "mid", "high", "enthusiast"):
                p = _make_profile(form_factor=ff, tier=tier, total_score=100, ram_gb=64)
                rec = _fallback_recommendation(p)
                assert rec.preset != "extreme", (
                    f"Fallback returned extreme for form_factor={ff}, tier={tier}"
                )


# ===========================================================================
# Unified recommend_preset() integration
# ===========================================================================


@pytest.mark.unit
class TestRecommendPreset:
    """Tests for the top-level recommend_preset() function."""

    def test_none_profile_returns_safe_fallback(self):
        rec = recommend_preset(None)
        assert rec.preset == "safe"
        assert rec.source == "fallback"

    def test_complete_profile_uses_primary(self):
        p = _make_profile(total_score=60, form_factor="desktop", ram_gb=16)
        rec = recommend_preset(p)
        assert rec.source == "primary"

    def test_incomplete_profile_uses_fallback(self):
        p = _make_profile(form_factor="unknown")
        rec = recommend_preset(p)
        assert rec.source == "fallback"

    def test_missing_ram_uses_fallback(self):
        p = _make_profile()
        p.ram = None  # type: ignore[assignment]
        rec = recommend_preset(p)
        assert rec.source == "fallback"

    def test_result_has_all_fields(self):
        p = _make_profile(total_score=55)
        rec = recommend_preset(p)
        assert isinstance(rec, Recommendation)
        assert rec.preset in ("safe", "competitive", "extreme")
        assert rec.reason
        assert rec.source in ("primary", "fallback")

    def test_dashboard_and_scripts_get_same_result(self):
        """Both views should get identical recommendations for the same profile."""
        profile = _make_profile(total_score=65, form_factor="desktop", ram_gb=16)
        rec_a = recommend_preset(profile)
        rec_b = recommend_preset(profile)
        assert rec_a.preset == rec_b.preset
        assert rec_a.source == rec_b.source
        assert rec_a.reason == rec_b.reason


# ===========================================================================
# Benchmark-miss scenarios (second-pass audit)
# ===========================================================================


@pytest.mark.unit
class TestBenchmarkMissRouting:
    """Verify that synthetic benchmark scores trigger the fallback path.

    The benchmark database returns default scores when hardware is not
    found (e.g. score 15 for Unknown CPU, score 10 for Unknown GPU).
    These should NOT be treated as real evidence.
    """

    def test_both_cpu_and_gpu_unmatched_uses_fallback(self):
        """Neither CPU nor GPU matched -> fallback regardless of other fields."""
        p = _make_profile(
            total_score=60,
            form_factor="desktop",
            ram_gb=16,
            cpu_matched=False,
            gpu_matched=False,
        )
        rec = recommend_preset(p)
        assert rec.source == "fallback"

    def test_cpu_matched_gpu_unmatched_uses_primary(self):
        """CPU matched alone is enough evidence for the primary path."""
        p = _make_profile(
            total_score=60,
            form_factor="desktop",
            ram_gb=16,
            cpu_matched=True,
            gpu_matched=False,
        )
        rec = recommend_preset(p)
        assert rec.source == "primary"

    def test_gpu_matched_cpu_unmatched_uses_primary(self):
        """GPU matched alone is enough evidence for the primary path."""
        p = _make_profile(
            total_score=60,
            form_factor="desktop",
            ram_gb=16,
            cpu_matched=False,
            gpu_matched=True,
        )
        rec = recommend_preset(p)
        assert rec.source == "primary"

    def test_both_matched_uses_primary(self):
        """Both CPU and GPU matched -> primary path (the normal happy path)."""
        p = _make_profile(
            total_score=60,
            form_factor="desktop",
            ram_gb=16,
            cpu_matched=True,
            gpu_matched=True,
        )
        rec = recommend_preset(p)
        assert rec.source == "primary"

    def test_unmatched_hardware_never_gets_extreme(self):
        """Even high scores with unmatched hardware must NOT yield extreme."""
        p = _make_profile(
            total_score=95,
            form_factor="desktop",
            tier="enthusiast",
            ram_gb=64,
            cpu_matched=False,
            gpu_matched=False,
        )
        rec = recommend_preset(p)
        assert rec.preset != "extreme"
        assert rec.source == "fallback"

    def test_unmatched_data_sufficiency_returns_false(self):
        """_has_sufficient_data should reject profiles with no benchmark matches."""
        p = _make_profile(
            total_score=70,
            form_factor="desktop",
            ram_gb=16,
            cpu_matched=False,
            gpu_matched=False,
        )
        assert _has_sufficient_data(p) is False

    def test_legacy_profile_without_benchmark_matched_treated_as_matched(self):
        """Profiles missing benchmark_matched attr should be treated as matched
        (backward compatibility — don't break callers using older SystemProfile)."""
        p = _make_profile(total_score=60, form_factor="desktop", ram_gb=16)
        # Remove benchmark_matched to simulate legacy profile
        del p.cpu.benchmark_matched  # type: ignore[attr-defined]
        del p.gpu.benchmark_matched  # type: ignore[attr-defined]
        assert _has_sufficient_data(p) is True
