"""
Help Content Manager
Manages loading and retrieving help content in multiple languages
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class HelpTopic:
    """Help topic with content"""
    id: str
    title: str
    icon: str
    content: Any
    language: str


class HelpManager:
    """Manages help content loading and retrieval"""

    def __init__(self, help_file: Path = None, language: str = "en"):
        """
        Initialize help manager

        Args:
            help_file: Path to help_content.json
            language: Default language (en or th)
        """
        if help_file is None:
            help_file = Path(__file__).parent.parent / "data" / "help_content.json"

        self.help_file = Path(help_file)
        self.language = language
        self.content = self._load_content()

    def _load_content(self) -> dict:
        """Load help content from JSON"""
        if self.help_file.exists():
            try:
                with open(self.help_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading help content: {e}")

        # Return empty structure if file doesn't exist
        return {"topics": {}}

    def get_topic(self, topic_id: str, language: str = None) -> Optional[HelpTopic]:
        """Get a help topic by ID"""
        lang = language or self.language

        if topic_id not in self.content.get("topics", {}):
            return None

        topic_data = self.content["topics"][topic_id]

        # Get content for requested language, fallback to English
        if lang in topic_data:
            content = topic_data[lang]
        elif "en" in topic_data:
            content = topic_data["en"]
        else:
            return None

        return HelpTopic(
            id=topic_id,
            title=content.get("title", topic_id),
            icon=content.get("icon", "ℹ️"),
            content=content,
            language=lang if lang in topic_data else "en"
        )

    def get_all_topics(self) -> list[HelpTopic]:
        """Get all help topics"""
        topics = []
        for topic_id in self.content.get("topics", {}):
            topic = self.get_topic(topic_id)
            if topic:
                topics.append(topic)
        return topics

    def get_profile_info(self, profile_name: str) -> Optional[dict]:
        """Get profile explanation"""
        profiles_topic = self.get_topic("profiles")
        if not profiles_topic:
            return None

        profiles = profiles_topic.content.get("profiles", {})
        return profiles.get(profile_name.upper())

    def get_script_info(self, script_name: str) -> Optional[dict]:
        """Get script description"""
        scripts_topic = self.get_topic("scripts")
        if not scripts_topic:
            return None

        categories = scripts_topic.content.get("categories", {})
        for cat_name, category in categories.items():
            scripts = category.get("scripts", {})
            if script_name in scripts:
                return scripts[script_name]
        return None

    def set_language(self, language: str):
        """Set current language"""
        self.language = language
