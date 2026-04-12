"""
Bundled Font Loader for ClutchG

Loads Figtree and Tabler Icons fonts from bundled TTF files at runtime
using the Windows GDI API (AddFontResourceEx via ctypes).

This replaces the previous tkextrafont-based approach which is broken
in PyInstaller frozen builds (GitHub Issue #10) and paths with spaces
(GitHub Issue #9).

AddFontResourceEx with FR_PRIVATE registers fonts only for the current
process — they are automatically unloaded when the process exits.

IMPORTANT: Tk root must exist before calling register_fonts() so that
tkinter.font.families() can verify the loaded fonts.
"""

import ctypes
import logging
import platform
import sys
from pathlib import Path
from typing import Optional

from core.paths import fonts_dir

logger = logging.getLogger(__name__)

# Windows GDI constants
FR_PRIVATE = 0x10  # Font is private to the calling process
FR_NOT_ENUM = 0x20  # Font will not appear in font enumeration

_font_dir: Optional[Path] = None  # Lazy — resolved on first use
_loaded_fonts: list[str] = []  # Paths of successfully loaded fonts
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


def _load_font_win32(font_path: Path, private: bool = True) -> bool:
    """
    Register a font file with Windows GDI using AddFontResourceEx.

    The font becomes available to the current process immediately and
    appears in tkinter.font.families().

    Args:
        font_path: Absolute path to the TTF file.
        private: If True, font is private to this process (auto-unloaded
                 on exit). If False, font is available system-wide until
                 explicitly removed.

    Returns:
        True if the font was loaded successfully.
    """
    try:
        path_str = str(font_path.resolve())
        path_buf = ctypes.create_unicode_buffer(path_str)
        flags = FR_PRIVATE if private else 0
        add_font = ctypes.windll.gdi32.AddFontResourceExW
        num_added = add_font(ctypes.byref(path_buf), flags, 0)
        return num_added > 0
    except (OSError, AttributeError) as e:
        logger.error(f"GDI AddFontResourceEx failed for {font_path.name}: {e}")
        return False


def _unload_font_win32(font_path_str: str, private: bool = True) -> bool:
    """
    Unregister a previously loaded font from Windows GDI.

    Args:
        font_path_str: The same path string used when loading.
        private: Must match the flag used when loading.

    Returns:
        True if the font was unloaded successfully.
    """
    try:
        path_buf = ctypes.create_unicode_buffer(font_path_str)
        flags = FR_PRIVATE if private else 0
        remove_font = ctypes.windll.gdi32.RemoveFontResourceExW
        return bool(remove_font(ctypes.byref(path_buf), flags, 0))
    except (OSError, AttributeError) as e:
        logger.debug(f"GDI RemoveFontResourceEx failed: {e}")
        return False


def register_fonts() -> bool:
    """
    Register bundled Figtree and Tabler Icons fonts.

    On Windows, uses the GDI API (AddFontResourceEx) which works
    reliably in both dev mode and PyInstaller frozen builds.

    On non-Windows platforms, logs a warning and returns False.
    (Cross-platform support could be added via fontconfig or Pillow
    pre-rendering in the future.)

    IMPORTANT: A Tk root window must exist before calling this function
    so that font availability can be verified.

    Returns:
        True if at least one font was loaded successfully.
    """
    global _loaded_fonts, _tabler_icons_loaded

    if sys.platform != "win32":
        logger.warning(
            "Font loading via GDI is Windows-only. "
            "Bundled fonts will not be available on this platform."
        )
        return False

    fonts_to_load = [
        "Figtree-Regular.ttf",
        "Figtree-Bold.ttf",
        "tabler-icons.ttf",
    ]

    success = False
    for filename in fonts_to_load:
        font_path = get_font_path(filename)
        if not font_path:
            logger.warning(f"Font file not found: {filename}")
            continue

        if _load_font_win32(font_path):
            _loaded_fonts.append(str(font_path.resolve()))
            logger.info(f"Loaded font via GDI: {filename}")
            success = True
            if "tabler-icons" in filename:
                _tabler_icons_loaded = True
        else:
            logger.error(f"Failed to load font via GDI: {filename}")

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
        Font family name to use.
    """
    global _font_family

    if _font_family is not None:
        return _font_family

    # Try to register if not already done
    if not _loaded_fonts:
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
    """
    Unload fonts (call on app exit).

    With FR_PRIVATE, Windows automatically unloads fonts when the
    process exits. This explicit cleanup is for orderly shutdown.
    """
    global _loaded_fonts, _font_family, _tabler_icons_loaded

    if sys.platform == "win32":
        for font_path_str in _loaded_fonts:
            _unload_font_win32(font_path_str)

    _loaded_fonts.clear()
    _font_family = None
    _tabler_icons_loaded = False
