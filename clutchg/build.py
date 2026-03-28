"""
ClutchG Build Script
Packages the application using PyInstaller
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


def build():
    """Build ClutchG executable"""

    # Paths
    project_dir = Path(__file__).parent
    src_dir = project_dir / "src"
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"

    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    print("=" * 60)
    print("Building ClutchG...")
    print("=" * 60)

    _ensure_pyinstaller()

    # Convert app icon PNG → ICO
    icon_png = src_dir / "assets" / "icon.png"
    icon_ico = build_dir / "icon.ico"
    icon_ico.parent.mkdir(parents=True, exist_ok=True)
    has_icon = icon_png.is_file() and _convert_icon(icon_png, icon_ico)

    # PyInstaller command
    # Note: --add-data uses the Windows path separator (;) intentionally;
    # this build script targets Windows only.
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=ClutchG",
        "--onefile",  # Single executable
        "--windowed",  # No console window
        "--uac-admin",  # Request admin privileges at launch
        # Hidden imports required by the runtime environment
        "--hidden-import=customtkinter",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=psutil",
        "--hidden-import=wmi",
        "--hidden-import=tkextrafont",
        "--collect-all=tkextrafont",
        # Output paths
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        # Entry point (must be last)
        str(src_dir / "main.py"),
    ]

    # Add icon flag if conversion succeeded
    if has_icon:
        cmd.insert(-1, f"--icon={icon_ico}")

    # Add data directories only if they exist
    config_dir = project_dir / "config"
    assets_dir = project_dir / "assets"
    fonts_dir = src_dir / "fonts"
    if config_dir.exists():
        cmd.insert(-1, f"--add-data={config_dir};config")
    if assets_dir.exists():
        cmd.insert(-1, f"--add-data={assets_dir};assets")
    if fonts_dir.exists():
        cmd.insert(-1, f"--add-data={fonts_dir};src/fonts")

    print("\nRunning PyInstaller...")
    print(" ".join(str(c) for c in cmd))
    print()

    result = subprocess.run(cmd, timeout=600)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("Build successful!")
        print("=" * 60)
        print(f"\nExecutable: {dist_dir / 'ClutchG.exe'}")

        # Copy batch scripts to dist
        batch_src = project_dir.parent / "src"
        batch_dst = dist_dir / "batch_scripts"
        if batch_src.exists():
            print("\nCopying batch scripts...")
            shutil.copytree(batch_src, batch_dst)
            print(f"Copied to: {batch_dst}")

        # Create README
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
            "## Support\n\n"
            "For issues, visit the project repository.\n\n"
            "---\nClutchG v1.0.0\n"
        )
        readme_file = dist_dir / "README.txt"
        readme_file.write_text(readme_content, encoding="utf-8")
        print(f"Created README: {readme_file}")

        # Show final executable size
        exe_path = dist_dir / "ClutchG.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable size: {size_mb:.1f} MB")

    else:
        print("\n" + "=" * 60)
        print("Build failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build()
