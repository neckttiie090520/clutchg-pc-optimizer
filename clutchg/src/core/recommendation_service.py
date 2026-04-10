"""
Recommendation Service - Single authoritative recommendation engine.

Provides one unified recommendation for which optimization preset to apply,
replacing the previous dual-path system where SystemDetector.recommend_profile()
and TweakRegistry.suggest_preset() could disagree.

Primary path: Score-based recommendation using total_score, form_factor, and RAM.
Fallback path: Conservative heuristic when hardware data is incomplete.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Recommendation:
    """Unified recommendation result consumed by all views."""

    preset: str  # 'safe', 'competitive', 'extreme'
    reason: str
    source: str  # 'primary' or 'fallback'
    total_score: Optional[int] = None
    confidence: Optional[float] = None


def _has_sufficient_data(profile) -> bool:
    """
    Check whether a SystemProfile has enough data for score-based recommendation.

    Minimum requirements:
    - total_score is a finite number
    - form_factor is known (not 'unknown')
    - RAM total_gb is available and positive
    - At least one of CPU or GPU was matched in the benchmark database
      (prevents synthetic default scores from triggering the primary path)
    """
    try:
        score = getattr(profile, "total_score", None)
        if score is None or not isinstance(score, (int, float)):
            return False

        form_factor = getattr(profile, "form_factor", "unknown")
        if form_factor == "unknown":
            return False

        ram = getattr(profile, "ram", None)
        if ram is None:
            return False
        ram_gb = getattr(ram, "total_gb", 0)
        if not isinstance(ram_gb, (int, float)) or ram_gb <= 0:
            return False

        # Require at least one real benchmark match — synthetic defaults are
        # not evidence.  If benchmark_matched is absent (legacy profiles),
        # we conservatively treat it as matched to avoid breaking callers.
        cpu = getattr(profile, "cpu", None)
        gpu = getattr(profile, "gpu", None)
        cpu_matched = getattr(cpu, "benchmark_matched", True) if cpu else False
        gpu_matched = getattr(gpu, "benchmark_matched", True) if gpu else False

        if not cpu_matched and not gpu_matched:
            return False

        return True
    except Exception:
        return False


def _primary_recommendation(profile) -> Recommendation:
    """
    Score-based recommendation (the main decision path).

    Thresholds adapted from the former TweakRegistry.suggest_preset() logic
    with an additional safety constraint: EXTREME requires desktop form factor.
    """
    total_score = profile.total_score
    form_factor = getattr(profile, "form_factor", "desktop")
    ram_gb = getattr(profile.ram, "total_gb", 0)

    if total_score >= 80 and form_factor == "desktop" and ram_gb >= 16:
        preset = "extreme"
        reason = "High-end desktop with 16 GB+ RAM -- maximum performance available"
        confidence = 0.9
    elif total_score >= 50 and ram_gb >= 8:
        preset = "competitive"
        reason = "Mid-range system with 8 GB+ RAM -- balanced gaming optimizations"
        confidence = 0.75
    else:
        preset = "safe"
        reason = "Safe optimizations recommended for your system configuration"
        confidence = 0.8

    return Recommendation(
        preset=preset,
        reason=reason,
        source="primary",
        total_score=total_score,
        confidence=confidence,
    )


def _fallback_recommendation(profile) -> Recommendation:
    """
    Conservative heuristic used when hardware data is incomplete.

    Rules:
    - Laptop -> SAFE always
    - Desktop with *some* positive signal -> COMPETITIVE at most
    - Never returns EXTREME (insufficient data = insufficient confidence)
    """
    form_factor = getattr(profile, "form_factor", "unknown")

    # Any laptop signal -> SAFE unconditionally
    if form_factor == "laptop":
        return Recommendation(
            preset="safe",
            reason="Laptop detected -- safe optimizations recommended",
            source="fallback",
            total_score=getattr(profile, "total_score", None),
            confidence=0.6,
        )

    # Desktop or unknown -- check for minimal positive evidence
    tier = getattr(profile, "tier", "entry")
    if tier in ("high", "enthusiast", "mid"):
        return Recommendation(
            preset="competitive",
            reason="Desktop detected with partial hardware data -- balanced profile",
            source="fallback",
            total_score=getattr(profile, "total_score", None),
            confidence=0.5,
        )

    # Truly minimal data -- stay safe
    return Recommendation(
        preset="safe",
        reason="Insufficient hardware data -- defaulting to safe optimizations",
        source="fallback",
        total_score=getattr(profile, "total_score", None),
        confidence=0.4,
    )


def recommend_preset(profile) -> Recommendation:
    """
    Single authoritative entry point for preset recommendation.

    Both dashboard and scripts views should call this instead of
    SystemDetector.recommend_profile() or TweakRegistry.suggest_preset().

    Args:
        profile: A SystemProfile (or compatible object).

    Returns:
        Recommendation with preset, reason, source, score, and confidence.
    """
    if profile is None:
        return Recommendation(
            preset="safe",
            reason="No system profile available -- defaulting to safe",
            source="fallback",
            confidence=0.3,
        )

    if _has_sufficient_data(profile):
        result = _primary_recommendation(profile)
        logger.info(
            "Recommendation (primary): preset=%s score=%s confidence=%.2f",
            result.preset,
            result.total_score,
            result.confidence or 0,
        )
    else:
        result = _fallback_recommendation(profile)
        logger.info(
            "Recommendation (fallback): preset=%s confidence=%.2f",
            result.preset,
            result.confidence or 0,
        )

    return result
