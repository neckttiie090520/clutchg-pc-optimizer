"""
Icon Provider - Centralized Icon Management
Uses Segoe MDL2 Assets as the canonical icon font on Windows.
Fallback chain: Segoe MDL2 Assets > Segoe UI Symbol > text labels.
"""

import platform
from typing import Dict, Optional


class IconProvider:
    """
    Centralized icon management for ClutchG.

    All codepoints target Segoe MDL2 Assets (ships with Windows 10/11).
    On non-Windows platforms the font won't be present, so callers
    should use get_icon_with_fallback() for graceful degradation.
    """

    # Segoe MDL2 Assets codepoints
    ICONS = {
        # Navigation
        "dashboard": "\ue80f",  # Home
        "home": "\ue80f",  # Home
        "profiles": "\ue713",  # Settings (gear)
        "scripts": "\ue756",  # CommandPrompt
        "backup": "\ue74e",  # Save
        "restore": "\ue777",  # Sync
        "help": "\ue897",  # Help
        "settings": "\ue713",  # Settings (gear)
        "docs": "\ue8a5",  # Library
        # Actions
        "create": "\ue710",  # Add
        "add": "\ue710",  # Add
        "delete": "\ue74d",  # Delete
        "edit": "\ue70f",  # Edit
        "save": "\ue74e",  # Save
        "cancel": "\ue711",  # Cancel
        "confirm": "\ue73e",  # CheckMark
        "apply": "\ue73e",  # CheckMark
        # Status
        "success": "\ue73e",  # CheckMark
        "error": "\ue711",  # Cancel
        "warning": "\ue7ba",  # Warning
        "info": "\ue946",  # Info
        "loading": "\ue72c",  # Refresh
        # States
        "check": "\ue73e",  # CheckMark
        "close": "\ue711",  # Cancel
        "expand": "\ue70d",  # ChevronDown
        "collapse": "\ue70e",  # ChevronUp
        "arrow_right": "\ue76c",  # ChevronRight
        "arrow_left": "\ue76b",  # ChevronLeft
        "arrow_down": "\ue70d",  # ChevronDown
        "arrow_up": "\ue70e",  # ChevronUp
        # System
        "cpu": "\ue7f4",  # Processing
        "gpu": "\ue7f8",  # TVMonitor
        "ram": "\ue964",  # DeviceLaptopNoPic (memory analogy)
        "storage": "\ue74e",  # Save / HardDrive
        "network": "\ue839",  # NetworkTower
        # UI Elements
        "search": "\ue721",  # Search
        "filter": "\ue71c",  # Filter
        "sort": "\ue8cb",  # Sort
        "more": "\ue712",  # More
        "menu": "\ue700",  # GlobalNavigationButton
        # Backup/Restore specific
        "history": "\ue81c",  # History
        "backup_restore": "\ue777",  # Sync
        "system_snapshot": "\ue7c1",  # Shield
        # Files/Folders
        "folder": "\ue8b7",  # FolderOpen
        "file": "\ue8a5",  # Page
        "document": "\ue8a5",  # Page
        # Material Symbols Outlined codepoints (used for content icons)
        "rocket_launch": "\ue559",  # Getting Started
        "bar_chart": "\ue26b",  # Dashboard topic
        "tune": "\ue429",  # Profiles topic / Tune
        "extension": "\ue87b",  # Optimization Center topic
        "bolt": "\ue929",  # Quick Actions / Power / Extreme
        "description": "\ue873",  # Scripts topic
        "shield": "\ue914",  # Safety topic / Safe profile
        "target": "\uf2c4",  # Profile recommendations
        "lightbulb": "\ue0a3",  # Tips
        "lan": "\ue639",  # Network category
        "build": "\ue869",  # Troubleshooting / Custom tab
        "menu_book": "\ue8ca",  # Glossary tab
        "download": "\ue2c4",  # Import
        "upload": "\ue2c6",  # Export
        "play_arrow": "\ue037",  # Run button
        "open_in_new": "\ue89e",  # External link
        "expand_more": "\ue5cf",  # Glossary expand arrow
        "check_circle": "\ue86c",  # Backup with restore point
        "inventory_2": "\ue1d7",  # Registry-only backup
        "refresh": "\ue5d5",  # Restart indicator
        "backup": "\ue860",  # Backup (cloud-upload style)
    }

    def __init__(self):
        """Initialize icon provider and detect available fonts"""
        self.system = platform.system()
        self._segmdl2_available = self._check_segmdl2()

    def _check_segmdl2(self) -> bool:
        """Check if Segoe MDL2 Assets font is available (Windows only)."""
        if self.system != "Windows":
            return False
        return self._is_font_available("Segoe MDL2 Assets")

    @staticmethod
    def _is_font_available(family_name: str) -> bool:
        """
        Check if a font family is installed by querying tkinter font families.

        Args:
            family_name: Font family name to check

        Returns:
            True if font is available, False otherwise
        """
        try:
            import tkinter.font as tkfont

            available = tkfont.families()
            return family_name in available
        except Exception:
            return False

    def get_icon(self, icon_name: str) -> str:
        """
        Get icon character for the given name.

        Args:
            icon_name: Name of the icon (from ICONS dict)

        Returns:
            Icon character as string, or empty string if not found
        """
        return self.ICONS.get(icon_name, "")

    def get_icon_font(self, icon_name: Optional[str] = None) -> tuple:
        """
        Get the icon font family tuple.

        Returns Segoe MDL2 Assets on Windows, otherwise a system fallback.

        Args:
            icon_name: Unused — kept for API compatibility

        Returns:
            Tuple of font family name(s)
        """
        if self._segmdl2_available:
            return ("Segoe MDL2 Assets",)

        # Fallback chain per platform
        if self.system == "Windows":
            return ("Segoe UI Symbol",)
        elif self.system == "Darwin":
            return ("Apple Color Emoji", "Arial Unicode MS")
        else:
            return ("Noto Color Emoji", "DejaVu Sans")

    def get_icon_with_fallback(self, icon_name: str, fallback_text: str = "") -> tuple:
        """
        Get icon character and font with fallback support.

        Args:
            icon_name: Name of the icon
            fallback_text: Text to use if icon unavailable

        Returns:
            Tuple of (icon_char, font_family)
        """
        icon_char = self.get_icon(icon_name)

        if not icon_char and fallback_text:
            return (fallback_text, "Segoe UI")

        font_family = self.get_icon_font(icon_name)[0]
        return (icon_char, font_family)

    def is_icon_available(self, icon_name: str) -> bool:
        """
        Check if an icon is available.

        Args:
            icon_name: Name of the icon to check

        Returns:
            True if icon exists in ICONS dict
        """
        return icon_name in self.ICONS

    def get_all_icons(self) -> Dict[str, str]:
        """
        Get all available icons.

        Returns:
            Dictionary of icon_name -> icon_character
        """
        return self.ICONS.copy()


# Singleton instance for easy access
_icon_provider_instance = None


def get_icon_provider() -> IconProvider:
    """
    Get singleton instance of IconProvider.

    Returns:
        IconProvider instance
    """
    global _icon_provider_instance
    if _icon_provider_instance is None:
        _icon_provider_instance = IconProvider()
    return _icon_provider_instance


# Convenience functions for quick access
def get_icon(icon_name: str) -> str:
    """Quick access to get icon character"""
    return get_icon_provider().get_icon(icon_name)


def get_icon_font(icon_name: Optional[str] = None) -> tuple:
    """Quick access to get icon font"""
    return get_icon_provider().get_icon_font(icon_name)
