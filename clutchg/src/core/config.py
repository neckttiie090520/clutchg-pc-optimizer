"""
Configuration Manager
Handles loading, saving, and managing application configuration
"""

import json
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir: Path = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Configuration directory (default: ./config)
        """
        if config_dir is None:
            # Default to config directory relative to project root
            config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "default_config.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration
        
        Returns:
            Configuration dictionary
        """
        # Start with default config
        config = self.get_default_config()
        
        # Load from file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
        
        # Override with user config if exists
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load user config: {e}")
        
        return config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to user config file
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error: Failed to save config: {e}")
            return False
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        Reset configuration to defaults
        
        Returns:
            Default configuration dictionary
        """
        # Remove user config
        if self.user_config_file.exists():
            self.user_config_file.unlink()
        
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            "version": "1.0.0",
            "language": "en",
            "theme": "modern",
            "accent": "tokyo_blue",  # Accent color preset
            "auto_backup": True,
            "confirm_actions": True,
            "log_level": "INFO",
            "batch_scripts_dir": "../src",  # Relative to clutchg/
            "backup_dir": "./data/backups",
            "max_backups": 10,
            "default_profile": "SAFE",
            "window_size": {
                "width": 1000,
                "height": 700
            },
            "startup_checks": {
                "check_admin": True,
                "detect_system": True,
                "verify_scripts": True
            }
        }
