"""
Configuration Manager
Handles loading, saving, and managing application configuration
"""

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Dict, Any

from core.paths import config_dir as _default_config_dir


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_dir: Path = None):
        """
        Initialize configuration manager

        Args:
            config_dir: Configuration directory (default: ./config)
        """
        if config_dir is None:
            # Default to config directory from centralized paths
            config_dir = _default_config_dir()

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "default_config.json"
        self.user_config_file = self.config_dir / "user_config.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Serialise writers. The updater records its last-check time from a
        # background thread while the settings view saves from the GUI thread, so
        # two os.replace calls can target user_config.json at once. On Windows
        # that loses one save with a bare log line rather than corrupting the
        # file, which is a silent settings loss for the user.
        self._write_lock = threading.Lock()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration with schema validation

        Returns:
            Configuration dictionary
        """
        # Start with default config
        config = self.get_default_config()

        # Load from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")

        # Override with user config if exists
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load user config: {e}")

        # BUG-013 FIX: Validate config against schema
        config = self._validate_config(config)

        return config

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration against schema.
        Rejects invalid keys and corrects type mismatches.

        BUG-013 FIX: Ensures config values match expected types.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validated configuration dictionary
        """
        schema = self.get_default_config()
        validated = {}

        for key, default_value in schema.items():
            if key in config:
                user_value = config[key]
                # Check type match (handle nested dicts recursively)
                if isinstance(default_value, dict) and isinstance(user_value, dict):
                    validated[key] = self._validate_config_recursive(
                        user_value, default_value
                    )
                elif type(user_value) == type(default_value):
                    validated[key] = user_value
                else:
                    print(
                        f"Warning: Invalid type for '{key}', expected {type(default_value).__name__}, using default"
                    )
                    validated[key] = default_value
            else:
                validated[key] = default_value

        return validated

    def _validate_config_recursive(self, user_dict: Dict, schema_dict: Dict) -> Dict:
        """Recursively validate nested config dictionaries."""
        validated = {}
        for key, default_value in schema_dict.items():
            if key in user_dict:
                user_value = user_dict[key]
                if isinstance(default_value, dict) and isinstance(user_value, dict):
                    validated[key] = self._validate_config_recursive(
                        user_value, default_value
                    )
                elif type(user_value) == type(default_value):
                    validated[key] = user_value
                else:
                    print(
                        f"Warning: Invalid type for '{key}', expected {type(default_value).__name__}, using default"
                    )
                    validated[key] = default_value
            else:
                validated[key] = default_value
        return validated

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to the user config file atomically.

        A direct overwrite that is interrupted leaves truncated JSON, which
        ``load_config`` cannot parse — it warns and silently falls back to
        defaults, so every user setting is lost without any visible error.
        Writing to a temporary file in the same directory and replacing the
        target means a reader sees either the old config or the new one.

        Args:
            config: Configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        with self._write_lock:
            temporary_path = None
            try:
                handle, temporary_name = tempfile.mkstemp(
                    dir=self.config_dir, prefix=".user_config-", suffix=".tmp"
                )
                temporary_path = Path(temporary_name)
                with os.fdopen(handle, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temporary_path, self.user_config_file)
                temporary_path = None
                return True
            except Exception as e:
                print(f"Error: Failed to save config: {e}")
                return False
            finally:
                if temporary_path is not None and temporary_path.exists():
                    try:
                        temporary_path.unlink()
                    except OSError:
                        pass

    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Reset configuration to defaults

        Returns:
            Default configuration dictionary
        """
        # Same lock as save_config: deleting the file is a write to the same
        # target, so it must not interleave with a concurrent save.
        with self._write_lock:
            if self.user_config_file.exists():
                try:
                    self.user_config_file.unlink()
                except OSError as e:
                    print(f"Warning: Failed to remove user config: {e}")

        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            "version": "1.0.4",
            "language": "en",
            "theme": "modern",
            "accent": "sunvalley",  # Accent color preset
            "auto_backup": True,
            "confirm_actions": True,
            "log_level": "INFO",
            "batch_scripts_dir": "../src",  # Relative to clutchg/
            "backup_dir": "./data/backups",
            "max_backups": 10,
            "default_profile": "SAFE",
            "window_size": {"width": 1000, "height": 700},
            "startup_checks": {
                "check_admin": True,
                "detect_system": True,
                "verify_scripts": True,
            },
            # Accessibility settings
            "reduce_motion": False,  # Reduce animations for motion-sensitive users
            "high_contrast": False,  # High contrast mode for accessibility
            # Auto-update settings
            "check_updates": True,  # Check for new versions on startup
            "last_update_check": 0.0,  # Unix timestamp of last check (float)
        }
