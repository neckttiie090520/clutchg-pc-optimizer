# -*- mode: python ; coding: utf-8 -*-
#
# ClutchG.spec — PyInstaller spec file for ClutchG PC Optimizer
#
# Build with:
#   cd clutchg
#   python build.py
#
# Or directly:
#   pyinstaller ClutchG.spec
#
# Output: dist/ClutchG/ClutchG.exe  (--onedir bundle)
#
# ──────────────────────────────────────────────────────────────────────────────
# DESIGN DECISIONS
#   - --onedir (not --onefile): Inno Setup creates the single installer,
#     so there is no benefit to --onefile's slow extraction overhead.
#   - upx=False: UPX corrupts DLLs (tkinter, pywin32). Never enable.
#   - batch_scripts are NOT bundled inside _MEIPASS. They live alongside
#     the exe so Inno Setup can install them to Program Files and they
#     remain writable/updatable.
#   - Writable data (config, logs, backups) goes to %APPDATA%/ClutchG
#     via paths.py — never inside the bundle.
# ──────────────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ---------------------------------------------------------------------------
# Directory anchors
# ---------------------------------------------------------------------------

# This spec file lives at clutchg/ClutchG.spec
SPEC_DIR   = Path(SPECPATH)          # clutchg/
SRC_DIR    = SPEC_DIR / "src"        # clutchg/src/
BUILD_DIR  = SPEC_DIR / "build"      # clutchg/build/  (work path)

# ---------------------------------------------------------------------------
# Icon (build.py converts PNG→ICO and drops it in build/)
# ---------------------------------------------------------------------------

_icon_ico = BUILD_DIR / "icon.ico"
_icon_arg = str(_icon_ico) if _icon_ico.exists() else None

# ---------------------------------------------------------------------------
# Data files to bundle into _MEIPASS
#
# Each entry:  (source_path_or_glob, dest_folder_inside_bundle)
#
# paths.py expects these relative to sys._MEIPASS:
#   assets/       <- hw-cpu.png, hw-gpu.png, hw-ram.png, icon.png
#   fonts/        <- *.ttf
#   data/         <- help_content.json, risk_explanations.json
# ---------------------------------------------------------------------------

datas = []

# 1. Application assets (PNG images)
_assets = SRC_DIR / "assets"
if _assets.exists():
    datas.append((str(_assets), "assets"))

# 1b. Bundle icon.ico into assets/ so iconbitmap() works at runtime
if _icon_ico.exists():
    datas.append((str(_icon_ico), "assets"))

# 2. Bundled fonts (TTF)
_fonts = SRC_DIR / "fonts"
if _fonts.exists():
    datas.append((str(_fonts), "fonts"))

# 3. Read-only JSON data files
_data = SRC_DIR / "data"
if _data.exists():
    datas.append((str(_data), "data"))

# 4. customtkinter — must collect its full package (theme JSON, images, etc.)
_ctk_datas, _ctk_binaries, _ctk_hiddenimports = collect_all("customtkinter")
datas     += _ctk_datas
binaries   = _ctk_binaries

# 5. tkextrafont — REMOVED (replaced by Windows GDI AddFontResourceEx in
#    font_loader.py — no external dependency needed for font loading)

# ---------------------------------------------------------------------------
# Hidden imports
#
# Modules that PyInstaller's static analysis misses because they are
# imported dynamically or via __import__ / importlib.
# ---------------------------------------------------------------------------

hiddenimports = [
    # --- CustomTkinter ---
    "customtkinter",
    *_ctk_hiddenimports,

    # --- Tkinter internals ---
    "_tkinter",
    "tkinter",
    "tkinter.font",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
    "PIL._tkinter_finder",

    # --- psutil ---
    "psutil",
    "psutil._pswindows",
    "psutil._psutil_windows",

    # --- pywin32 ---
    "win32api",
    "win32con",
    "win32com",
    "win32com.client",
    "pythoncom",
    "pywintypes",
    "winerror",

    # --- WMI ---
    "wmi",

    # --- CPU info ---
    "cpuinfo",
    "cpuinfo._cpuinfo",

    # --- Pillow ---
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",

    # --- stdlib that can be missed in windowed mode ---
    "logging.handlers",
    "queue",
    "threading",
    "subprocess",
    "json",
    "pathlib",
    "datetime",
    "traceback",
    "webbrowser",
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

a = Analysis(
    [str(SRC_DIR / "main.py")],
    pathex=[str(SRC_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude large packages we definitely don't use
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "IPython",
        "jupyter",
        "notebook",
        "setuptools",
        "pip",
        "pytest",
        "unittest",
    ],
    noarchive=False,
    optimize=0,
)

# ---------------------------------------------------------------------------
# PYZ archive (pure-Python modules)
# ---------------------------------------------------------------------------

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# EXE
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # --onedir: binaries go into COLLECT
    name="ClutchG",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                  # NEVER enable — corrupts DLLs
    console=False,              # --windowed: no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,             # Request elevation on Windows
    icon=_icon_arg,
    version=str(SPEC_DIR / "version_info.txt"),
)

# ---------------------------------------------------------------------------
# COLLECT — assembles the dist/ClutchG/ directory
# ---------------------------------------------------------------------------

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ClutchG",
)
