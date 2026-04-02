"""
Icon Provider - Centralized Icon Management

Two icon font systems:
  1. Segoe MDL2 Assets  — navigation & system icons (ships with Win 10/11)
  2. Tabler Icons       — content / topic icons (bundled with app, tabler-icons.ttf)

get_icon_font(icon_name) returns the correct font for each icon.
Fallback chain per font: Segoe MDL2 > Segoe UI Symbol > text labels.
"""

import platform
from typing import Dict, Optional


class IconProvider:
    """
    Centralized icon management for ClutchG.

    Icons are split into two font families:
      - SEGOE_ICONS:  Segoe MDL2 Assets codepoints (nav, actions, status, system)
      - TABLER_ICONS: Tabler Icons codepoints (content / topic icons, bundled TTF)

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

    # ── Tabler Icons codepoints (tabler-icons.ttf, v3.41.1) ──────────
    TABLER_ICONS: Dict[str, str] = {
        "rocket_launch": "\uec45",  # rocket
        "bar_chart": "\uea59",  # chart-bar
        "tune": "\uec38",  # adjustments-horizontal
        "extension": "\ueb10",  # puzzle
        "bolt": "\uea38",  # bolt
        "description": "\uf028",  # file-description
        "shield": "\ueb24",  # shield
        "target": "\ueb35",  # target
        "lightbulb": "\uea51",  # bulb
        "lan": "\uf09f",  # network
        "build": "\ueb40",  # tool
        "menu_book": "\uea39",  # book
        "download": "\uea96",  # download
        "upload": "\ueb47",  # upload
        "play_arrow": "\ued46",  # player-play
        "open_in_new": "\uea99",  # external-link
        "expand_more": "\uea5f",  # chevron-down
        "check_circle": "\uea67",  # circle-check
        "inventory_2": "\uea45",  # box
        "refresh": "\ueb13",  # refresh
        "backup_cloud": "\uea75",  # cloud-upload
        # Profile icons
        "verified_user": "\ueb22",  # shield-check (Safe profile)
        "speed": "\ueab1",  # gauge (Competitive profile)
        "local_fire_department": "\uec2c",  # flame (Extreme profile)
        # Compare / Preview
        "compare_arrows": "\uf1f4",  # arrows-exchange
        "star": "\ueb2e",  # star (Recommended badge)
        "visibility": "\uea9a",  # eye
        "arrow_forward_ms": "\uea1f",  # arrow-right
        "arrow_back_ms": "\uea19",  # arrow-left
        # Welcome overlay step & highlight icons
        "waving_hand": "\uec2e",  # hand-stop
        "dashboard_ms": "\ueac1",  # home
        "backup_ms": "\ueb62",  # device-floppy
        "restore_ms": "\ufafd",  # restore
        "history_ms": "\uebea",  # history
    }

    # ── Merged lookup (kept for backward compat) ──────────────────────
    ICONS: Dict[str, str] = {**SEGOE_ICONS, **TABLER_ICONS}

    TABLER_FONT = "Tabler Icons"
    SEGOE_FONT = "Segoe MDL2 Assets"

    def __init__(self):
        """Initialize icon provider and detect available fonts."""
        self.system = platform.system()
        self._segmdl2_available = self._check_font(self.SEGOE_FONT)
        self._tabler_available = self._check_font(self.TABLER_FONT)

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

    def _is_tabler_icon(self, icon_name: str) -> bool:
        """Return True if icon_name belongs to the Tabler Icons set."""
        return icon_name in self.TABLER_ICONS

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

        Returns Tabler Icons for content icons,
        Segoe MDL2 Assets for navigation/system icons.

        Args:
            icon_name: Name of the icon. If None, defaults to Segoe MDL2.

        Returns:
            Tuple of font family name(s)
        """
        # Tabler Icons path
        if icon_name and self._is_tabler_icon(icon_name):
            if self._tabler_available:
                return (self.TABLER_FONT,)
            # Tabler font missing — fall through to generic fallback
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
