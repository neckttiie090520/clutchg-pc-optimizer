# Test script for ClutchG Help system functionality
"""
Phase 10 Testing: Help System Unit Tests
Tests HelpManager, language switching, search, and edge cases.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Ensure clutchg/src is on sys.path so imports work under pytest
_src = Path(__file__).parent.parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from core.help_manager import HelpManager, HelpTopic


@pytest.mark.unit
class TestHelpManager:
    """Test HelpManager class"""

    def test_load_content_valid(self):
        """Test loading valid help content"""
        manager = HelpManager()
        assert manager.content is not None
        assert "topics" in manager.content

    def test_load_content_missing_file(self):
        """Test graceful handling of missing file"""
        manager = HelpManager(help_file=Path("/nonexistent/path.json"))
        assert manager.content == {"topics": {}}

    def test_get_topic_english(self):
        """Test getting topic in English"""
        manager = HelpManager(language="en")
        topic = manager.get_topic("getting_started")
        assert topic is not None
        assert topic.id == "getting_started"
        assert topic.language == "en"
        assert "Welcome" in topic.title or "Getting Started" in topic.title

    def test_get_topic_thai(self):
        """Test getting topic in Thai"""
        manager = HelpManager(language="th")
        topic = manager.get_topic("getting_started")
        assert topic is not None
        assert topic.language == "th"
        # Thai title should contain Thai characters
        assert any(ord(c) > 127 for c in topic.title), (
            "Thai title should have Thai chars"
        )

    def test_language_fallback(self):
        """Test fallback to English for unsupported language"""
        manager = HelpManager(language="fr")  # French not supported
        topic = manager.get_topic("getting_started")
        assert topic is not None
        # Should fall back to English
        assert topic.language == "en"

    def test_get_unknown_topic(self):
        """Test handling of unknown topic ID"""
        manager = HelpManager()
        topic = manager.get_topic("nonexistent_topic_xyz")
        assert topic is None

    def test_get_all_topics(self):
        """Test getting all topics"""
        manager = HelpManager()
        topics = manager.get_all_topics()
        assert len(topics) > 0
        topic_ids = [t.id for t in topics]
        assert "getting_started" in topic_ids
        assert "profiles" in topic_ids
        assert "safety" in topic_ids

    def test_set_language(self):
        """Test language switching"""
        manager = HelpManager(language="en")
        assert manager.language == "en"

        manager.set_language("th")
        assert manager.language == "th"

        topic = manager.get_topic("about")
        assert topic.language == "th"

    def test_get_profile_info(self):
        """Test getting profile information"""
        manager = HelpManager()
        safe_info = manager.get_profile_info("SAFE")
        assert safe_info is not None
        assert "description" in safe_info
        assert "risk_level" in safe_info

    def test_get_script_info(self):
        """Test getting script information"""
        manager = HelpManager()
        script_info = manager.get_script_info("power-manager-enhanced.bat")
        assert script_info is not None
        assert "description" in script_info

    def test_thai_encoding(self):
        """Test Thai text encoding is correct"""
        manager = HelpManager(language="th")
        topic = manager.get_topic("getting_started")
        assert topic is not None

        # Get the content and check for common Thai characters
        content = topic.content
        sections = content.get("sections", [])
        if sections:
            first_section = sections[0]
            heading = first_section.get("heading", "")
            # Check that heading contains valid Thai (not garbled)
            # Thai unicode range: 0x0E00 - 0x0E7F
            thai_chars = [c for c in heading if 0x0E00 <= ord(c) <= 0x0E7F]
            assert len(thai_chars) > 0, "Should contain Thai characters"

    def test_corrupted_json_handling(self):
        """Test handling of corrupted JSON file"""
        # Create a temp file with invalid JSON
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json content }}}")
            temp_path = Path(f.name)

        try:
            manager = HelpManager(help_file=temp_path)
            # Should not crash, return empty structure
            assert manager.content == {"topics": {}}
        finally:
            temp_path.unlink()
