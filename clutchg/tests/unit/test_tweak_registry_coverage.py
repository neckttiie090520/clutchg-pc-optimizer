"""
Unit Tests for TweakRegistry - Coverage Expansion

Tests for untested methods: suggest_preset, get_category_stats, get_compatible_tweaks
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.tweak_registry import get_tweak_registry, TweakRegistry, Tweak
from core.system_info import SystemProfile, OSInfo, CPUInfo, GPUInfo, RAMInfo, StorageInfo


@pytest.fixture
def registry():
    """Get TweakRegistry instance"""
    return get_tweak_registry()


def make_system_profile(tier="mid", total_score=50, ram_gb=16, form_factor="desktop"):
    """Helper to create SystemProfile with nested dataclasses"""
    return SystemProfile(
        os=OSInfo(platform="windows", version="10.0", build="19045", architecture="x64"),
        cpu=CPUInfo(name="Test CPU", vendor="intel", cores=4, threads=8, base_clock=3.0, score=15),
        gpu=GPUInfo(name="Test GPU", vendor="nvidia", vram=8, driver_version="1.0", score=15),
        ram=RAMInfo(total_gb=ram_gb, type="ddr4", speed=3200, score=10),
        storage=StorageInfo(primary_type="ssd", total_gb=500, score=10),
        form_factor=form_factor,
        tier=tier,
        total_score=total_score
    )


@pytest.mark.unit
class TestSuggestPreset:
    """Test suggest_preset() method"""

    def test_suggest_preset_returns_dict(self, registry):
        """Test that suggest_preset returns a dictionary"""
        profile = make_system_profile(tier="entry", total_score=25)
        
        result = registry.suggest_preset(profile)
        
        # Returns dict with expected keys
        assert isinstance(result, dict)
        assert "preset" in result
        assert "reason" in result
        assert "tweak_count" in result
        assert "compatible_count" in result

    def test_suggest_preset_entry_tier(self, registry):
        """Test preset suggestion for entry-level system"""
        profile = make_system_profile(tier="entry", total_score=25, ram_gb=4)
        
        result = registry.suggest_preset(profile)
        
        # Entry tier should get safe
        assert result["preset"] == "safe"

    def test_suggest_preset_mid_tier(self, registry):
        """Test preset suggestion for mid-tier system"""
        profile = make_system_profile(tier="mid", total_score=50, ram_gb=16)
        
        result = registry.suggest_preset(profile)
        
        # Mid tier should get competitive
        assert result["preset"] == "competitive"

    def test_suggest_preset_high_tier(self, registry):
        """Test preset suggestion for high-tier system"""
        profile = make_system_profile(tier="high", total_score=65, ram_gb=32)
        
        result = registry.suggest_preset(profile)
        
        # High tier should get competitive (score 65 < 80 threshold for extreme)
        assert result["preset"] in ["competitive", "extreme"]

    def test_suggest_preset_enthusiast_tier(self, registry):
        """Test preset suggestion for enthusiast system"""
        profile = make_system_profile(tier="enthusiast", total_score=95, ram_gb=64)
        
        result = registry.suggest_preset(profile)
        
        # Enthusiast tier should get extreme
        assert result["preset"] == "extreme"


@pytest.mark.unit
class TestGetCategoryStats:
    """Test get_category_stats() method"""

    def test_get_category_stats_returns_dict(self, registry):
        """Test that get_category_stats returns a dictionary"""
        stats = registry.get_category_stats()
        
        assert isinstance(stats, dict)
        assert len(stats) > 0

    def test_get_category_stats_has_valid_categories(self, registry):
        """Test that stats contain valid category names"""
        stats = registry.get_category_stats()
        
        # Should have common categories
        expected_categories = ["telemetry", "power", "gpu", "network", "services"]
        
        for cat in expected_categories:
            if cat in stats:
                assert isinstance(stats[cat], int)
                assert stats[cat] >= 0

    def test_get_category_stats_counts_match_tweaks(self, registry):
        """Test that category counts match actual tweak counts"""
        stats = registry.get_category_stats()
        all_tweaks = registry.get_all_tweaks()
        
        # Total from stats should match total tweaks
        total_from_stats = sum(stats.values())
        assert total_from_stats == len(all_tweaks)

    def test_get_category_stats_no_zero_categories(self, registry):
        """Test that all categories have at least one tweak"""
        stats = registry.get_category_stats()
        
        for category, count in stats.items():
            assert count > 0, f"Category {category} has 0 tweaks"


@pytest.mark.unit
class TestGetCompatibleTweaks:
    """Test get_compatible_tweaks() method"""

    def test_get_compatible_tweaks_windows_10(self, registry):
        """Test getting tweaks compatible with Windows 10"""
        profile = make_system_profile()
        # Override OS to be Windows 10
        profile.os = OSInfo(platform="windows", version="10.0", build="19045", architecture="x64")
        
        compatible = registry.get_compatible_tweaks(profile)
        
        # Should return a list
        assert isinstance(compatible, list)
        
        # All returned tweaks should be compatible with Win10
        for tweak in compatible:
            assert "10" in tweak.compatible_os or len(tweak.compatible_os) == 0

    def test_get_compatible_tweaks_windows_11(self, registry):
        """Test getting tweaks compatible with Windows 11"""
        profile = make_system_profile()
        # Override OS to be Windows 11
        profile.os = OSInfo(platform="windows", version="11.0", build="22000", architecture="x64")
        
        compatible = registry.get_compatible_tweaks(profile)
        
        # Should return a list
        assert isinstance(compatible, list)
        
        # All returned tweaks should be compatible with Win11
        for tweak in compatible:
            assert "11" in tweak.compatible_os or len(tweak.compatible_os) == 0

    def test_get_compatible_tweaks_returns_subset(self, registry):
        """Test that get_compatible_tweaks returns subset of all tweaks"""
        profile = make_system_profile()
        
        all_tweaks = registry.get_all_tweaks()
        compatible = registry.get_compatible_tweaks(profile)
        
        # Compatible should be <= all tweaks
        assert len(compatible) <= len(all_tweaks)

    def test_get_compatible_tweaks_nvidia_gpu(self, registry):
        """Test filtering with NVIDIA GPU"""
        profile = make_system_profile()
        profile.gpu = GPUInfo(name="NVIDIA RTX 3060", vendor="nvidia", vram=12, driver_version="1.0", score=25)
        
        compatible = registry.get_compatible_tweaks(profile)
        
        # Should return a list
        assert isinstance(compatible, list)

    def test_get_compatible_tweaks_amd_gpu(self, registry):
        """Test filtering with AMD GPU"""
        profile = make_system_profile()
        profile.gpu = GPUInfo(name="AMD Radeon RX 6700", vendor="amd", vram=10, driver_version="1.0", score=20)
        
        compatible = registry.get_compatible_tweaks(profile)
        
        # Should return a list
        assert isinstance(compatible, list)


@pytest.mark.unit
class TestGetTweaksForPreset:
    """Test get_tweaks_for_preset() method"""

    def test_get_tweaks_for_safe_preset(self, registry):
        """Test getting tweaks for SAFE preset"""
        tweaks = registry.get_tweaks_for_preset("safe")
        
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0
        
        # All should have preset_safe=True
        for tweak in tweaks:
            assert tweak.preset_safe is True

    def test_get_tweaks_for_competitive_preset(self, registry):
        """Test getting tweaks for COMPETITIVE preset"""
        tweaks = registry.get_tweaks_for_preset("competitive")
        
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0
        
        # All should have preset_competitive=True
        for tweak in tweaks:
            assert tweak.preset_competitive is True

    def test_get_tweaks_for_extreme_preset(self, registry):
        """Test getting tweaks for EXTREME preset"""
        tweaks = registry.get_tweaks_for_preset("extreme")
        
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0
        
        # All should have preset_extreme=True
        for tweak in tweaks:
            assert tweak.preset_extreme is True

    def test_preset_escalation(self, registry):
        """Test that higher presets include more tweaks"""
        safe_tweaks = registry.get_tweaks_for_preset("safe")
        comp_tweaks = registry.get_tweaks_for_preset("competitive")
        extreme_tweaks = registry.get_tweaks_for_preset("extreme")
        
        # EXTREME should have most tweaks
        assert len(extreme_tweaks) >= len(comp_tweaks)
        assert len(comp_tweaks) >= len(safe_tweaks)

    def test_get_tweaks_for_invalid_preset(self, registry):
        """Test getting tweaks for invalid preset name"""
        tweaks = registry.get_tweaks_for_preset("INVALID")
        
        # Should return empty list
        assert isinstance(tweaks, list)
        assert len(tweaks) == 0


@pytest.mark.unit
class TestGetTweaksByCategory:
    """Test get_tweaks_by_category() method"""

    def test_get_tweaks_by_category_telemetry(self, registry):
        """Test getting telemetry tweaks"""
        tweaks = registry.get_tweaks_by_category("telemetry")
        
        assert isinstance(tweaks, list)
        
        # All should be telemetry category
        for tweak in tweaks:
            assert tweak.category == "telemetry"

    def test_get_tweaks_by_category_power(self, registry):
        """Test getting power tweaks"""
        tweaks = registry.get_tweaks_by_category("power")
        
        assert isinstance(tweaks, list)
        
        for tweak in tweaks:
            assert tweak.category == "power"

    def test_get_tweaks_by_invalid_category(self, registry):
        """Test getting tweaks for non-existent category"""
        tweaks = registry.get_tweaks_by_category("nonexistent")
        
        # Should return empty list
        assert isinstance(tweaks, list)
        assert len(tweaks) == 0


@pytest.mark.unit
class TestGetRiskDistribution:
    """Test get_risk_distribution() method"""

    def test_get_risk_distribution_returns_dict(self, registry):
        """Test that get_risk_distribution returns a dictionary"""
        dist = registry.get_risk_distribution()
        
        assert isinstance(dist, dict)
        assert "LOW" in dist
        assert "MEDIUM" in dist
        assert "HIGH" in dist

    def test_get_risk_distribution_counts_match(self, registry):
        """Test that risk counts match actual tweaks"""
        dist = registry.get_risk_distribution()
        all_tweaks = registry.get_all_tweaks()
        
        total_from_dist = sum(dist.values())
        assert total_from_dist == len(all_tweaks)

    def test_get_risk_distribution_all_non_negative(self, registry):
        """Test that all risk counts are non-negative"""
        dist = registry.get_risk_distribution()
        
        for risk, count in dist.items():
            assert count >= 0


@pytest.mark.unit
class TestBuildCustomPreset:
    """Test build_custom_preset() method"""

    def test_build_custom_preset_valid_ids(self, registry):
        """Test building preset with valid tweak IDs"""
        # Get some real tweak IDs
        all_tweaks = registry.get_all_tweaks()
        tweak_ids = [t.id for t in all_tweaks[:3]]
        
        result = registry.build_custom_preset(tweak_ids)
        
        assert isinstance(result, dict)
        assert "tweaks" in result
        assert "count" in result
        assert result["count"] == 3

    def test_build_custom_preset_invalid_ids(self, registry):
        """Test building preset with invalid tweak IDs"""
        tweak_ids = ["invalid_tweak_1", "invalid_tweak_2"]
        
        result = registry.build_custom_preset(tweak_ids)
        
        assert isinstance(result, dict)
        assert result["count"] == 0
        assert len(result["warnings"]) > 0

    def test_build_custom_preset_mixed_ids(self, registry):
        """Test building preset with mix of valid and invalid IDs"""
        all_tweaks = registry.get_all_tweaks()
        valid_id = all_tweaks[0].id if all_tweaks else "valid"
        tweak_ids = [valid_id, "invalid_id"]
        
        result = registry.build_custom_preset(tweak_ids)
        
        assert isinstance(result, dict)
        assert result["count"] >= 1
        assert len(result["warnings"]) >= 1  # Warning for invalid ID

    def test_build_custom_preset_risk_calculation(self, registry):
        """Test that max_risk is calculated correctly"""
        # Get tweaks with different risk levels
        all_tweaks = registry.get_all_tweaks()
        low_risk = [t for t in all_tweaks if t.risk_level == "LOW"]
        high_risk = [t for t in all_tweaks if t.risk_level == "HIGH"]
        
        if low_risk and high_risk:
            tweak_ids = [low_risk[0].id, high_risk[0].id]
            result = registry.build_custom_preset(tweak_ids)
            
            # Max risk should be HIGH
            assert result["max_risk"] == "HIGH"
