"""
Unit Tests for Batch Script Parser

Migrated from test_core.py to use pytest framework.
Tests batch script discovery, parsing, categories, and metadata.
Updated: 2026-02-11 (Enhanced categories, tags, CATEGORY_META)
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.batch_parser import BatchParser, BatchScript, CATEGORY_META


# Module-level fixtures (available to all test classes)
@pytest.fixture
def scripts_dir():
    """Get scripts directory path"""
    # Use relative path from test file
    return Path(__file__).parent.parent.parent.parent / "src"


@pytest.fixture
def parser(scripts_dir):
    """Get BatchParser instance"""
    return BatchParser(scripts_dir)


@pytest.mark.unit
class TestBatchParser:

    def test_parser_initialization(self, scripts_dir):
        """Test that BatchParser can be initialized"""
        parser = BatchParser(scripts_dir)
        assert parser is not None
        assert parser.scripts_dir == scripts_dir

    def test_discover_scripts(self, parser):
        """Test script discovery finds scripts"""
        scripts = parser.discover_scripts()

        assert isinstance(scripts, list)
        # Should find at least 20 scripts from bat/src/
        assert len(scripts) >= 20, f"Expected >= 20 scripts, found {len(scripts)}"

    def test_script_has_required_fields(self, parser):
        """Test that discovered scripts have all required fields"""
        scripts = parser.discover_scripts()
        assert len(scripts) > 0

        for script in scripts:
            assert script.name is not None and len(script.name) > 0
            assert script.path is not None and script.path.exists()
            assert script.category is not None and len(script.category) > 0
            assert script.risk_level in ["LOW", "MEDIUM", "HIGH"]
            assert isinstance(script.requires_admin, bool)
            assert isinstance(script.requires_restart, bool)
            assert isinstance(script.estimated_time, int) and script.estimated_time > 0
            assert isinstance(script.tags, list) and len(script.tags) > 0

    def test_script_categories(self, parser):
        """Test that scripts are spread across multiple categories"""
        scripts = parser.discover_scripts()
        categories = set(s.category for s in scripts)

        # Should have diverse categories
        assert len(categories) >= 5, f"Expected >= 5 categories, got {categories}"

        # These categories should definitely exist
        expected = {"power", "bcdedit", "network", "profile", "backup", "safety"}
        found = categories & expected
        assert len(found) >= 4, f"Expected at least 4 of {expected}, found {found}"

    def test_script_paths_exist(self, parser):
        """Test that discovered script paths exist"""
        scripts = parser.discover_scripts()

        for script in scripts:
            assert script.path.exists(), f"Script file does not exist: {script.path}"

    def test_script_names_are_meaningful(self, parser):
        """Test that script names are descriptive"""
        scripts = parser.discover_scripts()

        for script in scripts:
            assert len(script.name) > 0
            assert script.name.isprintable()

    def test_tags_field(self, parser):
        """Test that tags field is populated correctly"""
        scripts = parser.discover_scripts()

        for script in scripts:
            assert isinstance(script.tags, list)
            assert len(script.tags) >= 1, f"Script {script.name} has no tags"
            # Category should always be in tags
            assert script.category in script.tags, (
                f"Script {script.name}: category '{script.category}' not in tags {script.tags}"
            )

    def test_risk_level_distribution(self, parser):
        """Test that risk levels are distributed reasonably"""
        scripts = parser.discover_scripts()
        risk_counts = {}
        for s in scripts:
            risk_counts[s.risk_level] = risk_counts.get(s.risk_level, 0) + 1

        # Should have all three levels
        assert "LOW" in risk_counts, "No LOW risk scripts found"
        assert "MEDIUM" in risk_counts, "No MEDIUM risk scripts found"
        assert "HIGH" in risk_counts, "No HIGH risk scripts found"


@pytest.mark.unit
class TestCategoryMeta:

    def test_category_meta_has_required_keys(self):
        """Test that CATEGORY_META entries have all required keys"""
        required_keys = {"icon", "color", "dim", "label"}

        for cat, meta in CATEGORY_META.items():
            for key in required_keys:
                assert key in meta, f"Category '{cat}' missing key '{key}'"

    def test_category_meta_covers_discovered_categories(self, parser):
        """Test that CATEGORY_META has entries for all discovered categories"""
        scripts = parser.discover_scripts()
        categories = set(s.category for s in scripts)

        for cat in categories:
            assert cat in CATEGORY_META, f"Category '{cat}' not in CATEGORY_META"

    def test_get_category_meta(self):
        """Test get_category_meta static method"""
        meta = BatchParser.get_category_meta("power")
        assert meta["label"] == "Power"
        assert meta["icon"] is not None

        # Unknown category should return 'other' fallback
        meta = BatchParser.get_category_meta("nonexistent")
        assert meta["label"] == "Other"

    def test_get_all_categories(self):
        """Test get_all_categories returns all known categories"""
        cats = BatchParser.get_all_categories()
        assert isinstance(cats, list)
        assert len(cats) >= 10
        assert "power" in cats
        assert "other" in cats


@pytest.mark.unit
class TestBatchParserIntegration:
    """Integration tests for batch parser"""

    def test_parser_with_nonexistent_directory(self):
        """Test parser with nonexistent directory"""
        nonexistent_dir = Path("/nonexistent/path")

        parser = BatchParser(nonexistent_dir)
        scripts = parser.discover_scripts()

        assert scripts == []

    def test_parser_with_empty_directory(self, tmp_path):
        """Test parser with empty directory"""
        parser = BatchParser(tmp_path)
        scripts = parser.discover_scripts()

        assert scripts == []

    def test_script_count_reasonable(self, parser):
        """Test that number of discovered scripts is reasonable"""
        scripts = parser.discover_scripts()

        assert len(scripts) >= 20
        assert len(scripts) <= 100

    def test_get_scripts_by_category(self, parser):
        """Test filtering scripts by category"""
        profile_scripts = parser.get_scripts_by_category("profile")
        assert len(profile_scripts) >= 2  # safe, competitive, extreme

        for s in profile_scripts:
            assert s.category == "profile"

    def test_get_category_counts(self, parser):
        """Test category counts method"""
        counts = parser.get_category_counts()
        assert isinstance(counts, dict)
        assert len(counts) >= 5
        assert sum(counts.values()) >= 20


@pytest.mark.unit
@pytest.mark.slow
class TestBatchParserPerformance:
    """Performance tests for batch parser"""

    def test_discovery_speed(self, parser):
        """Test that script discovery completes quickly"""
        import time

        start = time.time()
        scripts = parser.discover_scripts()
        elapsed = time.time() - start

        assert elapsed < 2.0
        assert scripts is not None
