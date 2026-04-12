"""
Bundled Font Loader for ClutchG
Loads Figtree and Tabler Icons fonts from bundled TTF files
at runtime using tkextrafont.

tkextrafont registers fonts directly with Tk's font system, so they
appear in tkinter.font.families() and work with CTkFont / CTkLabel etc.

IMPORTANT: Tk root must exist before calling register_fonts().
Call this after ctk.CTk() or tk.Tk() has been created.
"""

import logging
import platform
from pathlib import Path
from typing import Optional

from core.paths import fonts_dir

logger = logging.getLogger(__name__)

_font_dir: Optional[Path] = None  # Lazy — resolved on first use
_loaded_font_objects: list = []  # Keep references alive
_font_family: Optional[str] = None
_tabler_icons_loaded: bool = False


def _get_font_dir() -> Path:
    """Return the font directory, caching the result."""
    global _font_dir
    if _font_dir is None:
        _font_dir = fonts_dir()
    return _font_dir


def get_font_path(filename: str) -> Optional[Path]:
    """Get absolute path to a bundled font file."""
    path = _get_font_dir() / filename
    return path if path.exists() else None


def register_fonts() -> bool:
    """
    Register bundled Figtree and Tabler Icons fonts with Tk's
    font system.

    Uses tkextrafont to load TTF files directly into the Tk interpreter.
    The fonts become available in tkinter.font.families() immediately.

    IMPORTANT: A Tk root window must exist before calling this function.

    Returns:
        True if at least one font was loaded successfully
    """
    global _loaded_font_objects, _tabler_icons_loaded

    fonts_to_load = [
        "Figtree-Regular.ttf",
        "Figtree-Bold.ttf",
        "tabler-icons.ttf",
    ]

    try:
        from tkextrafont import Font
    except ImportError:
        logger.warning(
            "tkextrafont not installed. Bundled fonts will not be available. "
            "Install with: pip install tkextrafont"
        )
        return False

    success = False
    for filename in fonts_to_load:
        font_path = get_font_path(filename)
        if not font_path:
            logger.warning(f"Font file not found: {filename}")
            continue

        try:
            font_obj = Font(file=str(font_path.absolute()))
            _loaded_font_objects.append(font_obj)
            logger.info(f"Loaded font: {filename}")
            success = True
            if "tabler-icons" in filename:
                _tabler_icons_loaded = True
        except Exception as e:
            logger.error(f"Error loading font {filename}: {e}")

    return success


def is_tabler_icons_loaded() -> bool:
    """Return True if Tabler Icons was loaded from the bundle."""
    return _tabler_icons_loaded


def is_font_available(family: str) -> bool:
    """Check if a font family is available in Tk."""
    try:
        import tkinter as tk
        import tkinter.font as tkfont

        root = getattr(tk, "_default_root", None)
        if root is None:
            return False
        return family in tkfont.families(root)
    except Exception as e:
        logger.debug(f"Error checking font availability: {e}")
        return False


def ensure_fonts_loaded() -> str:
    """
    Ensure bundled fonts are loaded and return the family name to use.
    Falls back to system font if bundled fonts fail to load.

    Returns:
        Font family name to use
    """
    global _font_family

    if _font_family is not None:
        return _font_family

    # Try to register if not already done
    if not _loaded_font_objects:
        register_fonts()

    if is_font_available("Figtree"):
        logger.info("Using bundled Figtree font")
        _font_family = "Figtree"
        return _font_family

    # Fallback
    system = platform.system()
    fallback = {
        "Windows": "Segoe UI Variable",
        "Darwin": "SF Pro Text",
    }.get(system, "Inter")

    logger.info(f"Figtree not available, falling back to {fallback}")
    _font_family = fallback
    return _font_family


def cleanup_fonts():
    """Unload fonts (call on app exit)."""
    global _loaded_font_objects, _font_family, _tabler_icons_loaded
    for font_obj in _loaded_font_objects:
        try:
            font_obj.unload()
        except Exception:
            pass
    _loaded_font_objects.clear()
    _font_family = None
    _tabler_icons_loaded = False
