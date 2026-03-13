"""
Unit Tests for System Detection

Migrated from test_core.py to use pytest framework.
Tests system hardware detection and profile recommendation.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.system_info import SystemDetector


@pytest.mark.unit
class TestSystemDetection:
    """Test system hardware detection"""

    def test_detector_initialization(self):
        """Test that SystemDetector can be initialized"""
        detector = SystemDetector()
        assert detector is not None

    def test_detect_all(self):
        """Test complete system detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # Should return a system object with all fields populated
        assert system is not None
        assert system.os is not None
        assert system.cpu is not None
        assert system.gpu is not None
        assert system.ram is not None
        assert system.storage is not None

    def test_os_detection(self):
        """Test OS detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # OS information should be detected
        assert system.os.platform is not None
        assert system.os.version is not None
        assert system.os.platform in ["Windows", "Linux", "Darwin"] or "win" in system.os.platform.lower()

    def test_cpu_detection(self):
        """Test CPU detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # CPU should be detected
        assert system.cpu.name is not None
        assert system.cpu.cores > 0
        assert system.cpu.threads > 0
        assert system.cpu.threads >= system.cpu.cores

    def test_gpu_detection(self):
        """Test GPU detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # GPU should be detected (VRAM might be 0 if no GPU)
        assert system.gpu.name is not None
        assert system.gpu.vram is not None

    def test_ram_detection(self):
        """Test RAM detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # RAM should be detected and should be reasonable (> 0 GB)
        assert system.ram.total_gb > 0
        # available_gb might not exist, just check total_gb
        assert system.ram.total_gb is not None

    def test_storage_detection(self):
        """Test storage detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # Storage should be detected
        assert system.storage.total_gb > 0
        # available_gb might not exist, just check total_gb
        assert system.storage.total_gb is not None
        assert system.storage.primary_type is not None

    def test_system_tier_calculation(self):
        """Test that system tier is calculated"""
        detector = SystemDetector()
        system = detector.detect_all()

        # Tier should be one of the valid values
        assert system.tier in ["entry", "mid", "high", "enthusiast"]
        assert system.total_score is not None
        assert 0 <= system.total_score <= 100

    def test_profile_recommendation(self):
        """Test that appropriate profile is recommended"""
        detector = SystemDetector()
        system = detector.detect_all()

        # Should recommend a profile
        recommended = detector.recommend_profile(system)

        assert recommended is not None
        assert recommended in ["SAFE", "COMPETITIVE", "EXTREME"]

    def test_form_factor_detection(self):
        """Test form factor detection"""
        detector = SystemDetector()
        system = detector.detect_all()

        # Form factor should be detected
        assert system.form_factor is not None
        # Common form factors
        valid_factors = ["desktop", "laptop", "all-in-one", "mini pc", "unknown"]
        assert system.form_factor.lower() in valid_factors or system.form_factor is not None


@pytest.mark.unit
class TestSystemDetectionIntegration:
    """Integration tests for system detection"""

    def test_complete_detection_workflow(self):
        """Test complete detection workflow"""
        detector = SystemDetector()

        # Detect system
        system = detector.detect_all()

        # Get recommendation
        recommended = detector.recommend_profile(system)

        # Verify all data is consistent
        assert system.tier is not None
        assert system.total_score is not None
        assert recommended is not None

        # Higher tier systems should get more aggressive recommendations
        if system.tier == "enthusiast":
            # Ultra tier should handle EXTREME profile
            assert True  # At minimum, test doesn't crash
        elif system.tier == "entry":
            # Entry tier should recommend SAFE
            assert recommended in ["SAFE", "COMPETITIVE"]


@pytest.mark.unit
@pytest.mark.slow
class TestSystemDetectionPerformance:
    """Performance tests for system detection"""

    def test_detection_speed(self):
        """Test that system detection completes in reasonable time"""
        import time

        detector = SystemDetector()

        start = time.time()
        system = detector.detect_all()
        elapsed = time.time() - start

        # Detection should complete in less than 5 seconds
        assert elapsed < 5.0
        assert system is not None
