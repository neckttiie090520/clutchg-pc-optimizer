"""
Centralized Path Management for ClutchG

Provides two categories of paths:
1. **Bundled resources** (read-only) — assets, fonts, data files, batch scripts.
   In dev mode these resolve relative to the source tree.
   In frozen (PyInstaller) mode they resolve from sys._MEIPASS.

2. **Writable data** — config, logs, backups, snapshots, flight recorder.
   Always stored under %APPDATA%/ClutchG so they persist across updates
   and are never inside the read-only bundle.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Internal base paths
# ---------------------------------------------------------------------------


def _is_frozen() -> bool:
    """Return True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def _meipass() -> Path:
    """Return the PyInstaller temporary extraction directory."""
    return Path(sys._MEIPASS)  # type: ignore[attr-defined]


def _src_dir() -> Path:
    """Return the ``clutchg/src`` directory (dev mode only)."""
    return Path(__file__).resolve().parent.parent


def _project_dir() -> Path:
    """Return the ``clutchg/`` project directory (dev mode only)."""
    return _src_dir().parent


def _repo_root() -> Path:
    """Return the repository root ``bat/`` (dev mode only)."""
    return _project_dir().parent


# ---------------------------------------------------------------------------
# Public: bundled (read-only) resource helpers
# ---------------------------------------------------------------------------


def resource_path(relative: str) -> Path:
    """
    Resolve a *bundled* read-only resource to an absolute path.

    In dev mode the path is relative to ``clutchg/src/``.
    In frozen mode the path is relative to ``sys._MEIPASS``.

    Args:
        relative: Relative path from the src root,
                  e.g. ``"assets/icon.png"`` or ``"fonts/Figtree-Bold.ttf"``.

    Returns:
        Absolute ``Path`` to the resource.
    """
    if _is_frozen():
        return _meipass() / relative
    return _src_dir() / relative


def assets_dir() -> Path:
    """Return the directory containing PNG assets (icon, hw-cpu, etc.)."""
    return resource_path("assets")


def fonts_dir() -> Path:
    """Return the directory containing bundled TTF font files."""
    return resource_path("fonts")


def data_file(filename: str) -> Path:
    """
    Return the path to a bundled read-only data file.

    Args:
        filename: e.g. ``"help_content.json"`` or ``"risk_explanations.json"``.
    """
    return resource_path("data") / filename


def batch_scripts_dir() -> Path:
    """
    Return the directory containing batch optimization scripts.

    In dev mode: ``bat/src/`` (the repository ``src/`` folder).
    In frozen mode: ``<exe_dir>/batch_scripts/`` — Inno Setup copies
    the batch scripts alongside the exe directory.
    """
    if _is_frozen():
        # The exe lives at e.g. C:/Program Files/ClutchG/ClutchG.exe
        # Batch scripts are placed at C:/Program Files/ClutchG/batch_scripts/
        return Path(sys.executable).parent / "batch_scripts"
    return _repo_root() / "src"


def project_root() -> Path:
    """
    Return the ClutchG project directory.

    In dev mode: ``clutchg/``
    In frozen mode: the directory containing the exe.
    """
    if _is_frozen():
        return Path(sys.executable).parent
    return _project_dir()


def repo_root() -> Path:
    """
    Return the repository root directory.

    In dev mode: ``bat/``
    In frozen mode: falls back to exe directory (repo concept doesn't apply).
    """
    if _is_frozen():
        return Path(sys.executable).parent
    return _repo_root()


# ---------------------------------------------------------------------------
# Public: writable data directories (%APPDATA%/ClutchG)
# ---------------------------------------------------------------------------


def _appdata_base() -> Path:
    """
    Return the base writable directory for ClutchG user data.

    Uses ``%APPDATA%/ClutchG`` on Windows.
    Falls back to ``~/.clutchg`` on other platforms (testing).
    """
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "ClutchG"
    return Path.home() / ".clutchg"


def appdata_dir(subfolder: Optional[str] = None, *, create: bool = True) -> Path:
    """
    Return a writable directory under ``%APPDATA%/ClutchG``.

    In **dev mode** (not frozen), returns paths relative to the project
    tree so existing dev workflows are unchanged.  In **frozen mode**,
    returns paths under ``%APPDATA%/ClutchG``.

    Args:
        subfolder: Optional subdirectory, e.g. ``"logs"`` or ``"backups"``.
        create: If True (default), create the directory if it doesn't exist.

    Returns:
        Absolute ``Path`` to the writable directory.
    """
    if _is_frozen():
        base = _appdata_base()
    else:
        # Dev mode: keep current behavior — writable dirs under repo root
        base = _repo_root()

    if subfolder:
        result = base / subfolder
    else:
        result = base

    if create:
        result.mkdir(parents=True, exist_ok=True)

    return result


def config_dir(*, create: bool = True) -> Path:
    """Return the writable config directory."""
    if _is_frozen():
        return appdata_dir("config", create=create)
    return _project_dir() / "config"


def log_dir(*, create: bool = True) -> Path:
    """Return the writable log directory."""
    if _is_frozen():
        return appdata_dir("logs", create=create)
    return appdata_dir("data/logs", create=create)


def backup_dir(*, create: bool = True) -> Path:
    """Return the writable backup directory."""
    if _is_frozen():
        return appdata_dir("backups", create=create)
    return appdata_dir("data/backups", create=create)


def snapshot_dir(*, create: bool = True) -> Path:
    """Return the writable snapshot directory."""
    if _is_frozen():
        return appdata_dir("snapshots", create=create)
    # Dev mode: under clutchg/src/config/snapshots (existing location)
    d = _src_dir() / "config" / "snapshots"
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def flight_recorder_dir(*, create: bool = True) -> Path:
    """Return the writable flight recorder data directory."""
    if _is_frozen():
        return appdata_dir("flight_recorder", create=create)
    return appdata_dir("data/flight_recorder", create=create)


def custom_presets_file() -> Path:
    """Return the path to the custom presets JSON file."""
    if _is_frozen():
        d = appdata_dir("config", create=True)
    else:
        d = _src_dir() / "config"
        d.mkdir(parents=True, exist_ok=True)
    return d / "custom_presets.json"
