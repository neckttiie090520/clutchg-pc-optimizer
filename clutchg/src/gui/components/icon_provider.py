"""
Icon Provider - Centralized Icon Management

Single icon font system: Tabler Icons (bundled tabler-icons.ttf, v3.41.1)
All codepoints are in the Tabler range (ea00+).

Segoe MDL2 Assets kept only for chevron/arrow navigation glyphs that are
rendered by the OS title-bar / window chrome (not our app labels).

get_icon_font(icon_name) always returns "Tabler Icons" for content icons.
"""

import platform
from typing import Dict, Optional


class IconProvider:
    """
    Centralized icon management for ClutchG.

    All icons use the bundled Tabler Icons font (tabler-icons.ttf).
    SEGOE_ICONS kept for backward-compat key lookups only; codepoints
    are now Tabler so the font family returned is always "Tabler Icons".

    Use get_icon_with_fallback() for graceful degradation on non-Windows.
    """

    # ── Navigation / action icons — all Tabler codepoints ─────────────
    SEGOE_ICONS: Dict[str, str] = {
        # Navigation
        "dashboard": "\ueac1",  # home
        "home": "\ueac1",  # home
        "profiles": "\uf1f6",  # category
        "scripts": "\uf7fb",  # adjustments-bolt  (Optimize)
        "optimize": "\uf7fb",  # adjustments-bolt
        "backup": "\uf235",  # stack-push
        "restore": "\ufafd",  # restore
        "help": "\ufa0b",  # progress-help
        "settings": "\ueb20",  # settings-2
        "docs": "\uea39",  # book
        # Actions
        "create": "\uea9e",  # plus
        "add": "\uea9e",  # plus
        "delete": "\ueb55",  # trash
        "edit": "\uec9b",  # pencil
        "save": "\ueb62",  # device-floppy
        "cancel": "\ueb55",  # trash (fallback)
        "confirm": "\uea67",  # circle-check
        "apply": "\uea67",  # circle-check
        # Status
        "success": "\uea67",  # circle-check
        "error": "\uea87",  # circle-x
        "warning": "\uea35",  # alert-triangle
        "info": "\ueac5",  # info-circle
        "loading": "\ueb13",  # refresh
        # States
        "check": "\uea67",  # circle-check
        "close": "\ueb55",  # x
        "expand": "\uea5f",  # chevron-down
        "collapse": "\uea61",  # chevron-up
        "arrow_right": "\uea1f",  # arrow-right
        "arrow_left": "\uea19",  # arrow-left
        "arrow_down": "\uea5f",  # chevron-down
        "arrow_up": "\uea61",  # chevron-up
        # System hardware
        "cpu": "\ueb87",  # cpu
        "gpu": "\uf50d",  # device-desktop-analytics
        "ram": "\uefce",  # memory
        "storage": "\ueb2b",  # server
        "network": "\uf09f",  # network
        # UI Elements
        "search": "\ueb1c",  # search
        "filter": "\uea5a",  # filter
        "sort": "\ueb73",  # arrows-sort
        "more": "\uea37",  # dots
        "menu": "\uead0",  # menu-2
        # Backup/Restore specific
        "history": "\uebea",  # history
        "backup_restore": "\ufafd",  # restore
        "system_snapshot": "\ueb24",  # shield
        # Files/Folders
        "folder": "\uea83",  # folder
        "file": "\uea78",  # file
        "document": "\uf028",  # file-description
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
        "backup_ms": "\uf235",  # stack-push  (Backup nav)
        "restore_ms": "\ufafd",  # restore
        "history_ms": "\uebea",  # history
    }

    # ── Merged lookup (kept for backward compat) ──────────────────────
    ICONS: Dict[str, str] = {**SEGOE_ICONS, **TABLER_ICONS}

    TABLER_FONT = "Tabler Icons"
    SEGOE_FONT = "Segoe MDL2 Assets"  # kept for reference; no longer used for icons

    def __init__(self):
        """Initialize icon provider and detect available fonts."""
        self.system = platform.system()
        self._tabler_available = self._check_font(self.TABLER_FONT)
        # Segoe presence check kept for future use but not critical
        self._segmdl2_available = self._check_font(self.SEGOE_FONT)

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
        """All icons now use Tabler — return True for any known icon."""
        return icon_name in self.ICONS

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

        All icons now use Tabler Icons (bundled TTF). Segoe MDL2 no longer
        used for app content icons.

        Args:
            icon_name: Name of the icon (unused — kept for API compat).

        Returns:
            Tuple of font family name(s)
        """
        if self._tabler_available:
            return (self.TABLER_FONT,)
        # Fallback if font not loaded yet
        return ("Segoe UI",)

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
