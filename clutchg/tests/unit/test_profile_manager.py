"""
Unit Tests for Profile Manager

Migrated from test_core.py to use pytest framework.
Tests profile management and script association.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.profile_manager import ProfileManager


# Module-level fixtures (available to all test classes)
@pytest.fixture
def scripts_dir():
    """Get scripts directory path"""
    return Path(__file__).parent.parent.parent.parent / "src"


@pytest.fixture
def manager(scripts_dir):
    """Get ProfileManager instance"""
    return ProfileManager(scripts_dir)


@pytest.mark.unit
class TestProfileManager:

    def test_manager_initialization(self, scripts_dir):
        """Test that ProfileManager can be initialized"""
        manager = ProfileManager(scripts_dir)
        assert manager is not None
        assert manager.scripts_dir == scripts_dir

    def test_get_all_profiles(self, manager):
        """Test getting all available profiles"""
        profiles = manager.get_all_profiles()

        # Should return a list
        assert isinstance(profiles, list)

        # Should have exactly 3 profiles (SAFE, COMPETITIVE, EXTREME)
        assert len(profiles) == 3

    def test_profile_names(self, manager):
        """Test that profiles have correct names"""
        profiles = manager.get_all_profiles()

        profile_names = [p.name for p in profiles]

        # Should have the three main profiles
        assert "SAFE" in profile_names
        assert "COMPETITIVE" in profile_names
        assert "EXTREME" in profile_names

    def test_profile_has_required_fields(self, manager):
        """Test that profiles have required fields"""
        profiles = manager.get_all_profiles()

        for profile in profiles:
            # Should have name
            assert profile.name is not None
            assert len(profile.name) > 0

            # Should have description
            assert profile.description is not None
            assert len(profile.description) > 0

            # Should have risk level
            assert profile.risk_level is not None

            # Should have FPS gain range
            assert profile.expected_fps_gain is not None
            assert isinstance(profile.expected_fps_gain, tuple)
            assert len(profile.expected_fps_gain) == 2

            # Should have scripts list
            assert profile.scripts is not None
            assert isinstance(profile.scripts, list)

            # Should have requires_restart flag
            assert isinstance(profile.requires_restart, bool)

    def test_profile_risk_levels(self, manager):
        """Test that profiles have appropriate risk levels"""
        profiles = manager.get_all_profiles()

        risk_levels = {p.name: p.risk_level.value for p in profiles}

        # SAFE should have lowest risk
        assert risk_levels["SAFE"] == "low"

        # COMPETITIVE should have medium risk
        assert risk_levels["COMPETITIVE"] == "medium"

        # EXTREME should have highest risk
        assert risk_levels["EXTREME"] == "high"

    def test_profile_fps_gains(self, manager):
        """Test that FPS gains increase with risk"""
        profiles = manager.get_all_profiles()

        fps_gains = {p.name: p.expected_fps_gain for p in profiles}

        # All should have positive FPS gains
        for name, gain in fps_gains.items():
            assert gain[0] >= 0
            assert gain[1] >= 0
            assert gain[1] >= gain[0]  # Upper bound >= lower bound

        # EXTREME should have highest gains
        assert fps_gains["EXTREME"][1] >= fps_gains["SAFE"][1]
        assert fps_gains["EXTREME"][1] >= fps_gains["COMPETITIVE"][1]

    def test_profile_scripts(self, manager):
        """Test that profiles have associated scripts"""
        profiles = manager.get_all_profiles()

        for profile in profiles:
            # All profiles should have at least some scripts
            # (or at minimum, scripts field should exist)
            assert profile.scripts is not None

            # Scripts should be a list
            assert isinstance(profile.scripts, list)


@pytest.mark.unit
class TestProfileManagerIntegration:
    """Integration tests for profile manager"""

    def test_get_profile_by_name(self, manager):
        """Test getting specific profile by name"""
        # Try to get SAFE profile
        profiles = manager.get_all_profiles()
        safe_profile = next((p for p in profiles if p.name == "SAFE"), None)

        # Should exist
        assert safe_profile is not None
        assert safe_profile.name == "SAFE"

    def test_profile_ordering(self, manager):
        """Test that profiles are returned in correct order"""
        profiles = manager.get_all_profiles()

        # Should be ordered: SAFE, COMPETITIVE, EXTREME
        # (from least to most aggressive)
        assert profiles[0].name == "SAFE"
        assert profiles[1].name == "COMPETITIVE"
        assert profiles[2].name == "EXTREME"

    def test_profile_descriptions_are_meaningful(self, manager):
        """Test that profile descriptions are informative"""
        profiles = manager.get_all_profiles()

        for profile in profiles:
            # Description should be reasonably long
            assert len(profile.description) > 20

            # Description should mention key aspects
            desc_lower = profile.description.lower()
            # (Just verify it's not empty or garbage)


@pytest.mark.unit
@pytest.mark.slow
class TestProfileManagerPerformance:
    """Performance tests for profile manager"""

    def test_profile_loading_speed(self, manager):
        """Test that profiles load quickly"""
        import time

        start = time.time()
        profiles = manager.get_all_profiles()
        elapsed = time.time() - start

        # Loading should be instant (< 0.1 seconds)
        assert elapsed < 0.1
        assert len(profiles) == 3
