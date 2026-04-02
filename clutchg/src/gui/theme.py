"""
ClutchG Theme Configuration
Windows 11 Dark UI - Minimal Design with Glassmorphism
Updated: 2026-02-03 (Multi-Theme System)
"""

import platform
import customtkinter as ctk
from typing import Dict, Optional


# ============================================================================
# FONT FAMILIES - Uses bundled Figtree font
# ============================================================================
_ui_font_family: Optional[str] = None


def ui_family() -> str:
    """Get the UI font family. Uses bundled Figtree if available."""
    global _ui_font_family
    if _ui_font_family is None:
        from gui.font_loader import ensure_fonts_loaded

        _ui_font_family = ensure_fonts_loaded()
    return _ui_font_family


def mono_family() -> str:
    system = platform.system()
    if system == "Windows":
        return "Cascadia Mono"
    if system == "Darwin":
        return "SF Mono"
    return "JetBrains Mono"


# ============================================================================
# THEME DEFINITIONS
# ============================================================================
THEMES = {
    "dark": {
        # Backgrounds - Deeper, richer navy tones
        "bg_primary": "#0A0E1A",  # Deep navy (main background)
        "bg_secondary": "#131825",  # Slightly lighter navy
        "bg_card": "#1A2332",  # Card backgrounds
        "bg_tertiary": "#1A2332",  # Alias for bg_card
        "bg_card_hover": "#222B3F",  # Hover state
        "bg_hover": "#2A3447",  # General hover
        "bg_elevated": "#222B3F",  # Elevated elements
        "bg_active": "#323D54",  # Active state
        "bg_selected": "#3A4861",  # Selected state
        # Borders - More visible
        "border": "#2D3748",
        "border_subtle": "#2D3748",
        "border_medium": "#4A5568",
        "border_strong": "#718096",
        # Text - Better contrast
        "text_primary": "#FFFFFF",  # Pure white for headings
        "text_secondary": "#A0AEC0",  # Light gray for body
        "text_tertiary": "#8A9BB0",  # Muted text (improved contrast 4.8:1)
        "text_muted": "#4A5568",  # Very muted (labels, placeholders)
        "text_dim": "#384050",  # Dimmer than muted (decorative / disabled)
        # Focus indicators (WCAG 2.4.7)
        "focus_ring": "#7aa2f7",  # Focus ring color
        "focus_ring_offset": 2,  # Focus ring offset in pixels
        "focus_ring_width": 2,  # Focus ring border width
        # Glassmorphism - More transparent overlays
        "glass_bg": "#1A2332",
        "glass_border": "#2D3748",
        "glass_highlight": "#323942",
        "glass_light": "#1f2538",  # ~5% white on #1A2332
        "glass_medium": "#222940",  # ~8% white on #1A2332
        "glass_strong": "#283044",  # ~12% white on #1A2332
    },
    "zinc": {
        # Professional Monotone (Zinc/Slate)
        "bg_primary": "#09090b",  # Zinc 950
        "bg_secondary": "#18181b",  # Zinc 900
        "bg_card": "#18181b",  # Zinc 900
        "bg_tertiary": "#27272a",  # Zinc 800
        "bg_card_hover": "#27272a",  # Zinc 800
        "bg_hover": "#27272a",  # Zinc 800
        "bg_elevated": "#27272a",  # Zinc 800
        "bg_active": "#3f3f46",  # Zinc 700
        "bg_selected": "#3f3f46",  # Zinc 700
        # Borders - Sharp and subtle
        "border": "#27272a",  # Zinc 800
        "border_subtle": "#27272a",
        "border_medium": "#3f3f46",  # Zinc 700
        "border_strong": "#52525b",  # Zinc 600
        # Text - High contrast
        "text_primary": "#fafafa",  # Zinc 50
        "text_secondary": "#a1a1aa",  # Zinc 400
        "text_tertiary": "#a1a1aa",  # Zinc 400 (improved contrast)
        "text_muted": "#52525b",  # Zinc 600
        "text_dim": "#3f3f46",  # Zinc 700
        # Focus indicators (WCAG 2.4.7)
        "focus_ring": "#71717a",  # Focus ring color
        "focus_ring_offset": 2,
        "focus_ring_width": 2,
        # Glassmorphism
        "glass_bg": "#18181b",
        "glass_border": "#27272a",
        "glass_highlight": "#3f3f46",
        "glass_light": "#1d1d20",  # ~3% white on #18181b
        "glass_medium": "#212124",  # ~5% white on #18181b
        "glass_strong": "#2c2c2f",  # ~10% white on #18181b
    },
    "light": {
        # Backgrounds
        "bg_primary": "#F9F9F9",
        "bg_secondary": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "bg_tertiary": "#FFFFFF",
        "bg_card_hover": "#F0F0F0",
        "bg_hover": "#F5F5F5",
        "bg_elevated": "#FFFFFF",
        "bg_active": "#E8E8E8",
        "bg_selected": "#E0E0E0",
        # Borders
        "border": "#E0E0E0",
        "border_subtle": "#EBEBEB",
        "border_medium": "#D0D0D0",
        "border_strong": "#B0B0B0",
        # Text
        "text_primary": "#1A1A1A",
        "text_secondary": "#666666",
        "text_tertiary": "#555555",  # Improved contrast (5.2:1)
        "text_muted": "#999999",
        "text_dim": "#CCCCCC",
        # Focus indicators (WCAG 2.4.7)
        "focus_ring": "#2563eb",  # Blue focus ring
        "focus_ring_offset": 2,
        "focus_ring_width": 2,
        # Glassmorphism for light theme
        "glass_bg": "#FFFFFF",
        "glass_border": "#E5E5E5",
        "glass_highlight": "#F0F0F0",
        "glass_light": "#f7f7f7",  # ~3% black on #FFFFFF
        "glass_medium": "#f2f2f2",  # ~5% black on #FFFFFF
        "glass_strong": "#ebebeb",  # ~8% black on #FFFFFF
    },
    "modern": {
        # Sun Valley-inspired theme (Windows 11 dark)
        # Backgrounds - Pure neutral grays (no blue/purple tint)
        "bg_primary": "#1c1c1c",  # Sun Valley -bg
        "bg_secondary": "#272727",  # Elevated surface
        "bg_card": "#2d2d2d",  # Card backgrounds
        "bg_tertiary": "#383838",  # Higher elevation
        "bg_card_hover": "#333333",  # Card hover
        "bg_hover": "#333333",  # General hover
        "bg_elevated": "#2d2d2d",  # Elevated elements
        "bg_active": "#404040",  # Active/pressed state
        "bg_selected": "#404040",  # Selected state
        # Borders - Subtle gray
        "border": "#3d3d3d",
        "border_subtle": "#3d3d3d",
        "border_medium": "#555555",
        "border_strong": "#6e6e6e",
        # Text - Pure white/gray (no color tint)
        "text_primary": "#fafafa",  # Sun Valley -fg
        "text_secondary": "#b0b0b0",  # Body text
        "text_tertiary": "#999999",  # Muted text (5.3:1 contrast on #1c1c1c)
        "text_muted": "#595959",  # Sun Valley -disfg
        "text_dim": "#404040",  # Very muted
        # Focus indicators (WCAG 2.4.7)
        "focus_ring": "#57c8ff",  # Sun Valley -accent
        "focus_ring_offset": 2,
        "focus_ring_width": 2,
        # Glassmorphism - Neutral overlays
        "glass_bg": "#2d2d2d",
        "glass_border": "#3d3d3d",
        "glass_highlight": "#404040",
        "glass_light": "#222222",  # ~4% white on #1c1c1c
        "glass_medium": "#252525",  # ~7% white on #1c1c1c
        "glass_strong": "#292929",  # ~11% white on #1c1c1c
    },
}

# Accent color presets - More vibrant!
# Accent color presets - Monotone / Professional
# We use the same color for primary and secondary to achieve "Soild" look (no gradient)
ACCENT_PRESETS = {
    "white": {
        "primary": "#fafafa",
        "hover": "#ffffff",
        "pressed": "#e4e4e7",
        "dim": "#27272a",
        "text": "#18181b",
    },  # Dark text
    "zinc": {
        "primary": "#52525b",
        "hover": "#71717a",
        "pressed": "#3f3f46",
        "dim": "#18181b",
        "text": "#ffffff",
    },
    "blue": {
        "primary": "#2563eb",
        "hover": "#3b82f6",
        "pressed": "#1d4ed8",
        "dim": "#1e3a8a",
        "text": "#ffffff",
    },  # Professional Blue
    "cyan": {
        "primary": "#0891b2",
        "hover": "#06b6d4",
        "pressed": "#0e7490",
        "dim": "#164e63",
        "text": "#ffffff",
    },  # Professional Cyan
    "purple": {
        "primary": "#7c3aed",
        "hover": "#8b5cf6",
        "pressed": "#6d28d9",
        "dim": "#4c1d95",
        "text": "#ffffff",
    },
    "pink": {
        "primary": "#db2777",
        "hover": "#ec4899",
        "pressed": "#be185d",
        "dim": "#831843",
        "text": "#ffffff",
    },
    "red": {
        "primary": "#dc2626",
        "hover": "#ef4444",
        "pressed": "#b91c1c",
        "dim": "#7f1d1d",
        "text": "#ffffff",
    },
    "orange": {
        "primary": "#ea580c",
        "hover": "#f97316",
        "pressed": "#c2410c",
        "dim": "#7c2d12",
        "text": "#ffffff",
    },
    "green": {
        "primary": "#16a34a",
        "hover": "#22c55e",
        "pressed": "#15803d",
        "dim": "#14532d",
        "text": "#ffffff",
    },
    "teal": {
        "primary": "#0d9488",
        "hover": "#14b8a6",
        "pressed": "#0f766e",
        "dim": "#134e4a",
        "text": "#ffffff",
    },
    # Sun Valley-inspired accents
    "sunvalley": {
        "primary": "#57c8ff",
        "hover": "#6fd4ff",
        "pressed": "#3ba8e0",
        "dim": "#1a3040",
        "text": "#000000",
    },  # Sun Valley sky blue
    "sunvalley_blue": {
        "primary": "#2f60d8",
        "hover": "#4070e8",
        "pressed": "#2550c0",
        "dim": "#1a2850",
        "text": "#ffffff",
    },  # Sun Valley selection blue
}

# Default accent
DEFAULT_ACCENT = "sunvalley"


# ============================================================================
# THEME MANAGER
# ============================================================================
class ThemeManager:
    """Manages theme switching and color application"""

    # Map custom theme names to CTk-compatible appearance modes.
    # CTk only accepts "dark", "light", or "system".
    _APPEARANCE_MAP = {
        "dark": "dark",
        "zinc": "dark",
        "modern": "dark",
        "light": "light",
    }

    def __init__(self):
        self.current_theme = "modern"
        self.current_accent = DEFAULT_ACCENT
        self.color_cache = {}

    def get_colors(self, theme: str = None, accent: str = None) -> Dict[str, str]:
        """Get color palette for specified theme and accent"""
        theme = theme or self.current_theme
        accent = accent or self.current_accent

        cache_key = f"{theme}_{accent}"
        if cache_key in self.color_cache:
            return self.color_cache[cache_key].copy()

        # Start with base theme colors
        colors = THEMES[theme].copy()

        # Add accent colors
        accent_colors = ACCENT_PRESETS[accent]
        colors.update(
            {
                "accent": accent_colors["primary"],
                "accent_hover": accent_colors["hover"],
                "accent_pressed": accent_colors["pressed"],
                "accent_dim": accent_colors["dim"],
                "text_on_accent": accent_colors.get(
                    "text", "#ffffff"
                ),  # Dynamic text color
                "border_accent": accent_colors["primary"],
                # FORCE SOLID: Secondary accent matches primary (removes gradient effect)
                "accent_secondary": accent_colors["primary"],
            }
        )

        # Add status colors (theme-independent)
        colors.update(
            {
                "success": "#22C55E",
                "success_hover": "#2ED16A",
                "success_dim": "#1a2e1f",
                "warning": "#F59E0B",
                "warning_hover": "#F7B448",
                "warning_dim": "#2e2510",
                "danger": "#EF4444",
                "danger_hover": "#F16161",
                "danger_dim": "#2e1616",
                "info": "#57c8ff",
                "info_hover": "#6fd4ff",
                "info_dim": "#1a2e3a",
                # Risk Levels
                "risk_low": "#22C55E",
                "risk_medium": "#F59E0B",
                "risk_high": "#EF4444",
                # Score Colors
                "score_excellent": "#22C55E",
                "score_good": "#57c8ff",
                "score_average": "#F59E0B",
                "score_low": "#EF4444",
            }
        )

        # Cache and return
        self.color_cache[cache_key] = colors
        return colors

    def set_theme(self, theme: str, accent: str = None) -> Dict[str, str]:
        """Change current theme and update the module-level COLORS dict."""
        self.current_theme = theme
        if accent:
            self.current_accent = accent

        # Map custom theme name to a valid CTk appearance mode
        appearance = self._APPEARANCE_MAP.get(theme, "dark")
        ctk.set_appearance_mode(appearance)

        # Refresh module-level COLORS so all importers see new values (H-4)
        new_colors = self.get_colors()
        COLORS.clear()
        COLORS.update(new_colors)

        return new_colors

    def set_accent(self, accent: str) -> Dict[str, str]:
        """Change accent color only and refresh module-level COLORS."""
        self.current_accent = accent
        new_colors = self.get_colors()
        COLORS.clear()
        COLORS.update(new_colors)
        return new_colors

    def get_available_accents(self) -> list:
        """Get list of available accent color names"""
        return list(ACCENT_PRESETS.keys())

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(THEMES.keys())


# Global theme manager instance
theme_manager = ThemeManager()

# COLORS dict for backward compatibility
# Gets values from current theme
COLORS = theme_manager.get_colors()

# ============================================================================
# TYPOGRAPHY
# ============================================================================
FONTS = {
    # Display sizes (for hero text)
    "display_large": ("Figtree", 48, "bold"),
    "display_medium": ("Figtree", 36, "bold"),
    "display_small": ("Figtree", 28, "bold"),
    # Headings
    "h1": ("Figtree", 24, "bold"),
    "h2": ("Figtree", 20, "bold"),
    "h3": ("Figtree", 18, "bold"),
    "h4": ("Figtree", 16, "bold"),
    # Body text
    "body_large": ("Figtree", 16, "normal"),
    "body": ("Figtree", 14, "normal"),
    "body_small": ("Figtree", 12, "normal"),
    "body_bold": ("Figtree", 14, "bold"),
    # Special
    "caption": ("Figtree", 11, "normal"),
    "micro": ("Figtree", 10, "normal"),
    "overline": ("Figtree", 10, "bold"),
    "button": ("Figtree", 13, "bold"),
    "button_large": ("Figtree", 14, "bold"),
    # Legacy (for backward compatibility) - use Figtree directly to avoid early font loading
    "display": ("Figtree", 32, "bold"),
    "title": ("Figtree", 24, "bold"),
    "section": ("Figtree", 18, "bold"),
    "mono": (mono_family(), 12, "normal"),
}

# Typography constants — alias for FONTS to avoid duplication
# (FONTS is the canonical source; TYPOGRAPHY is kept for backward compatibility)
TYPOGRAPHY = FONTS


# ============================================================================
# SIZING
# ============================================================================
# ============================================================================
# SIZING (Refined)
# ============================================================================
SIZES = {
    "sidebar_width": 60,
    # DEPRECATED: Use RADIUS["xl"] / RADIUS["md"] directly.
    # Kept for backward compatibility — will be removed in a future release.
    "card_radius": 14,  # → RADIUS["xl"]
    "button_radius": 6,  # → RADIUS["md"]
    "button_height": 32,
    "button_height_sm": 28,
    "input_height": 32,
    "score_ring_size": 180,
    "score_ring_thickness": 12,
}

# Spacing system (Refined - Tighter)
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,  # Reduced from 16
    "lg": 20,  # Reduced from 24
    "xl": 28,  # Reduced from 32
    "2xl": 40,
    "3xl": 56,
}

# Border radius system
RADIUS = {
    "sm": 4,
    "md": 6,
    "lg": 10,
    "xl": 14,
    "2xl": 20,
    "full": 9999,
}


# ============================================================================
# ICONS (Windows Segoe MDL2 Assets - LEGACY)
# ============================================================================
# See: https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-ui-symbol-font
# NOTE: NAV_ICONS is kept for backward compatibility.
# Use IconProvider (from icon_provider.py) for new code.
NAV_ICONS = {
    "dashboard": "\ue80f",  # Home
    "profiles": "\ue9e9",  # Dial/Tune (Control panel style) - or E771
    "scripts": "\ue943",  # Document/Script
    "backup": "\uea35",  # CloudUpload or SaveLocal E74E
    "restore": "\ue81c",  # History
    "help": "\ue897",  # Help
    "settings": "\ue713",  # Settings
    "cpu": "\ue950",  # Processor
    "gpu": "\ue7fd",  # Gaming/GPU
    "ram": "\ue964",  # Memory
    "storage": "\ue8b7",  # HardDrive
    "safe": "\ue81e",  # Shield
    "competitive": "\ue76e",  # Lightning
    "extreme": "\ue7c5",  # Flame/Fire warning
}

# ============================================================================
# ICON PROVIDER INTEGRATION
# ============================================================================
# Convenience functions for accessing IconProvider
# These should be used instead of NAV_ICONS for new code
# ============================================================================

_icon_provider_instance = None


def get_icon_provider():
    """Get or create IconProvider singleton instance"""
    global _icon_provider_instance
    if _icon_provider_instance is None:
        from gui.components.icon_provider import IconProvider

        _icon_provider_instance = IconProvider()
    return _icon_provider_instance


def ICON(icon_name: str) -> str:
    """
    Get icon character from IconProvider.

    Usage:
        icon_char = ICON("backup")  # Returns: "\uf1c9"

    Args:
        icon_name: Name of the icon

    Returns:
        Icon character as string
    """
    return get_icon_provider().get_icon(icon_name)


def ICON_FONT(icon_name: str = None) -> tuple:
    """
    Get font family for icon from IconProvider.

    Usage:
        font_family = ICON_FONT()  # Returns: ("Material Symbols Outlined",)

    Args:
        icon_name: Optional icon name for specific font selection

    Returns:
        Tuple of (primary_font, fallback_fonts)
    """
    return get_icon_provider().get_icon_font(icon_name)


def get_icon_with_fallback(icon_name: str, fallback_text: str = "") -> tuple:
    """
    Get icon character and font with fallback support.

    Usage:
        icon, font = get_icon_with_fallback("backup", "Backup")

    Args:
        icon_name: Name of the icon
        fallback_text: Text to use if icon unavailable

    Returns:
        Tuple of (icon_char, font_family)
    """
    return get_icon_provider().get_icon_with_fallback(icon_name, fallback_text)


# ============================================================================
# ANIMATION TIMING
# ============================================================================
ANIMATION = {
    "instant": 50,  # Nearly instant
    "fast": 150,  # Quick transitions (hover effects)
    "normal": 300,  # Standard transitions (view switches)
    "slow": 500,  # Deliberate transitions (sidebar expand)
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_score_color(score: int) -> str:
    """Get color based on system score"""
    if score >= 80:
        return COLORS["score_excellent"]
    if score >= 60:
        return COLORS["score_good"]
    if score >= 40:
        return COLORS["score_average"]
    return COLORS["score_low"]


def get_risk_colors(level: str) -> dict:
    """Get risk level color set"""
    level_upper = level.upper()
    if level_upper == "LOW":
        return {"primary": COLORS["risk_low"], "dim": COLORS["success_dim"]}
    if level_upper in ("MEDIUM", "MED"):
        return {"primary": COLORS["risk_medium"], "dim": COLORS["warning_dim"]}
    if level_upper == "HIGH":
        return {"primary": COLORS["risk_high"], "dim": COLORS["danger_dim"]}
    return {"primary": COLORS["text_muted"], "dim": COLORS["bg_hover"]}


PROFILE_COLORS = {
    "SAFE": {"primary": COLORS["risk_low"], "dim": COLORS["success_dim"]},
    "COMPETITIVE": {"primary": COLORS["risk_medium"], "dim": COLORS["warning_dim"]},
    "EXTREME": {"primary": COLORS["risk_high"], "dim": COLORS["danger_dim"]},
}
