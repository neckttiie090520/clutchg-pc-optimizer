"""
Icon Provider - Centralized Icon Management

Two icon font systems:
  1. Segoe MDL2 Assets  — navigation & system icons (ships with Win 10/11)
  2. Material Symbols Outlined — content / topic icons (bundled with app)

get_icon_font(icon_name) returns the correct font for each icon.
Fallback chain per font: Segoe MDL2 > Segoe UI Symbol > text labels.
"""

import platform
from typing import Dict, Optional


class IconProvider:
    """
    Centralized icon management for ClutchG.

    Icons are split into two font families:
      - SEGOE_ICONS:    Segoe MDL2 Assets codepoints (nav, actions, status, system)
      - MATERIAL_ICONS: Material Symbols Outlined codepoints (content / topic icons)

    Use get_icon_with_fallback() for graceful degradation on non-Windows.
    """

    # ── Segoe MDL2 Assets codepoints ──────────────────────────────────
    SEGOE_ICONS: Dict[str, str] = {
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
    }

    # ── Material Symbols Outlined codepoints ──────────────────────────
    MATERIAL_ICONS: Dict[str, str] = {
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
        "backup_cloud": "\ue860",  # Backup (cloud-upload style)
        # Profile icons
        "verified_user": "\ue8e8",  # Safe profile
        "speed": "\ue3de",  # Competitive profile
        "local_fire_department": "\uef55",  # Extreme profile
        # Compare / Preview
        "compare_arrows": "\ue915",  # Compare panel toggle
        "star": "\ue838",  # Recommended badge
        "visibility": "\ue8f4",  # Preview button
        "arrow_forward_ms": "\ue5c8",  # Material forward arrow (nav)
        "arrow_back_ms": "\ue5c4",  # Material back arrow (nav)
        # Welcome overlay step & highlight icons
        "waving_hand": "\ue766",  # Welcome step icon
        "dashboard_ms": "\ue871",  # Home step icon (Material version)
        "backup_ms": "\ue864",  # Backup step icon (Material version)
        "restore_ms": "\ue929",  # Restore highlight icon (uses 'settings_backup_restore')
        "history_ms": "\ue889",  # History highlight icon (Material version)
    }

    # ── Merged lookup (kept for backward compat) ──────────────────────
    ICONS: Dict[str, str] = {**SEGOE_ICONS, **MATERIAL_ICONS}

    MATERIAL_FONT = "Material Symbols Outlined"
    SEGOE_FONT = "Segoe MDL2 Assets"

    def __init__(self):
        """Initialize icon provider and detect available fonts."""
        self.system = platform.system()
        self._segmdl2_available = self._check_font(self.SEGOE_FONT)
        self._material_available = self._check_font(self.MATERIAL_FONT)

    def _check_font(self, family_name: str) -> bool:
        """Check if a font family is available (Windows only for Segoe)."""
        if self.system != "Windows" and family_name == self.SEGOE_FONT:
            return False
        return self._is_font_available(family_name)

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

    def _is_material_icon(self, icon_name: str) -> bool:
        """Return True if icon_name belongs to the Material Symbols set."""
        return icon_name in self.MATERIAL_ICONS

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
        Get the correct icon font family tuple for the given icon.

        Returns Material Symbols Outlined for content icons,
        Segoe MDL2 Assets for navigation/system icons.

        Args:
            icon_name: Name of the icon. If None, defaults to Segoe MDL2.

        Returns:
            Tuple of font family name(s)
        """
        # Material Symbols path
        if icon_name and self._is_material_icon(icon_name):
            if self._material_available:
                return (self.MATERIAL_FONT,)
            # Material font missing — fall through to generic fallback
            return ("Segoe UI",)

        # Segoe MDL2 path (default)
        if self._segmdl2_available:
            return (self.SEGOE_FONT,)

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
