"""
ClutchG Build Script
Packages the application using PyInstaller via ClutchG.spec
"""

import subprocess
import sys
import shutil
from pathlib import Path


def _ensure_pyinstaller() -> None:
    """Install PyInstaller if it is not already available."""
    try:
        import PyInstaller  # noqa: F401

        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            timeout=120,
        )
        if result.returncode != 0:
            print("ERROR: Failed to install PyInstaller.")
            sys.exit(1)


def _convert_icon(png_path: Path, ico_path: Path) -> bool:
    """Convert a PNG to ICO with multiple sizes for Windows.

    Returns True on success, False on failure.
    """
    try:
        from PIL import Image

        img = Image.open(png_path)
        # Standard Windows icon sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, format="ICO", sizes=sizes)
        print(f"Icon generated: {ico_path}")
        return True
    except Exception as exc:
        print(f"WARNING: Could not convert icon ({exc}). Building without icon.")
        return False


def build() -> None:
    """Build ClutchG using ClutchG.spec (--onedir mode)."""

    # Paths
    project_dir = Path(__file__).parent  # clutchg/
    src_dir = project_dir / "src"  # clutchg/src/
    dist_dir = project_dir / "dist"  # clutchg/dist/
    build_dir = project_dir / "build"  # clutchg/build/
    spec_file = project_dir / "ClutchG.spec"

    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    print("=" * 60)
    print("Building ClutchG (onedir)...")
    print("=" * 60)

    _ensure_pyinstaller()

    # Convert app icon PNG → ICO before invoking PyInstaller.
    # ClutchG.spec reads build/icon.ico at analysis time.
    icon_png = src_dir / "assets" / "icon.png"
    icon_ico = build_dir / "icon.ico"
    icon_ico.parent.mkdir(parents=True, exist_ok=True)
    _convert_icon(icon_png, icon_ico)  # result embedded in .spec logic

    # Build using the spec file
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec_file),
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "--noconfirm",
    ]

    print("\nRunning PyInstaller...")
    print(" ".join(str(c) for c in cmd))
    print()

    result = subprocess.run(cmd, timeout=600)

    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("Build FAILED.")
        print("=" * 60)
        sys.exit(1)

    # ----------------------------------------------------------------
    # Post-build: copy batch scripts alongside the exe directory
    # ----------------------------------------------------------------
    # dist/ClutchG/           <- the onedir bundle
    #   ClutchG.exe
    #   batch_scripts/        <- bat/src/ copied here
    #   _internal/            <- Python runtime + deps
    # ----------------------------------------------------------------
    bundle_dir = dist_dir / "ClutchG"
    batch_src = project_dir.parent / "src"  # bat/src/
    batch_dst = bundle_dir / "batch_scripts"

    if batch_src.exists():
        print("\nCopying batch scripts...")
        shutil.copytree(batch_src, batch_dst)
        print(f"  {batch_src} -> {batch_dst}")
    else:
        print(f"WARNING: Batch scripts not found at {batch_src}")

    # ----------------------------------------------------------------
    # Post-build: write a plain-text README into the bundle dir
    # ----------------------------------------------------------------
    readme_content = (
        "# ClutchG - Windows PC Optimizer\n\n"
        "## Quick Start\n\n"
        '1. Right-click ClutchG.exe -> "Run as Administrator"\n'
        "2. Select an optimization profile (SAFE, COMPETITIVE, EXTREME)\n"
        '3. Click "Apply Profile"\n'
        "4. Restart your computer if prompted\n\n"
        "## Profiles\n\n"
        "- SAFE        - Minimal optimizations, maximum safety\n"
        "- COMPETITIVE - Balanced performance tuning\n"
        "- EXTREME     - Aggressive optimizations (advanced users)\n\n"
        "## System Requirements\n\n"
        "- Windows 10/11 (64-bit)\n"
        "- Administrator privileges\n"
        "- 100 MB disk space\n\n"
        "## User Data\n\n"
        "Config, logs, and backups are stored in:\n"
        "  %APPDATA%\\ClutchG\\\n\n"
        "## Support\n\n"
        "https://github.com/neckttiie090520/clutchg-pc-optimizer\n\n"
        "---\nClutchG v1.0.0\n"
    )
    readme_file = bundle_dir / "README.txt"
    readme_file.write_text(readme_content, encoding="utf-8")
    print(f"Created README: {readme_file}")

    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    exe_path = bundle_dir / "ClutchG.exe"
    print("\n" + "=" * 60)
    print("Build successful!")
    print("=" * 60)
    print(f"\nBundle directory : {bundle_dir}")
    print(f"Executable       : {exe_path}")

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Executable size  : {size_mb:.1f} MB")

        # Rough total bundle size
        total = sum(f.stat().st_size for f in bundle_dir.rglob("*") if f.is_file())
        print(f"Total bundle size: {total / (1024 * 1024):.1f} MB")

    print(
        "\nNext step: run installer/build-installer.bat to create the"
        " Inno Setup .exe installer."
    )


if __name__ == "__main__":
    build()
