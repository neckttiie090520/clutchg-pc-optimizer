"""
Google Material Symbols Font Installer for ClutchG
Automatically downloads and installs Material Symbols Outlined font on Windows
"""

import platform
import subprocess
import urllib.request
import os
from pathlib import Path


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == "Windows"


def download_material_symbols() -> Path:
    """
    Download Material Symbols Outlined font

    Returns:
        Path to downloaded font file
    """
    print("Downloading Google Material Symbols Outlined font...")

    # URL for Material Symbols Outlined variable font
    font_url = "https://github.com/google/material-design-icons/raw/mafont/VariableFont/MaterialSymbolsOutlined%5Bopsz,wght%5D.ttf"

    # Download to temp directory
    temp_dir = Path(os.environ.get("TEMP", "/tmp"))
    font_path = temp_dir / "MaterialSymbolsOutlined.ttf"

    try:
        urllib.request.urlretrieve(font_url, font_path)
        print(f"✓ Downloaded to: {font_path}")
        return font_path
    except Exception as e:
        print(f"✗ Download failed: {e}")
        raise


def install_font_on_windows(font_path: Path) -> bool:
    """
    Install font on Windows system

    Args:
        font_path: Path to .ttf font file

    Returns:
        True if successful, False otherwise
    """
    if not is_windows():
        print("This installer is for Windows only.")
        return False

    print("\nInstalling font...")

    try:
        # Windows fonts directory
        fonts_dir = Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "Fonts"
        dest_path = fonts_dir / "MaterialSymbolsOutlined.ttf"

        # Copy font to Windows fonts directory
        import shutil
        shutil.copy(font_path, dest_path)
        print(f"✓ Copied to: {dest_path}")

        # Add font registry entry
        import winreg

        # Open registry key for fonts
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            0,
            winreg.KEY_SET_VALUE
        )

        # Add font entry
        winreg.SetValueEx(key, "Material Symbols Outlined (TrueType)", 0, winreg.REG_SZ, "MaterialSymbolsOutlined.ttf")
        winreg.CloseKey(key)

        print("✓ Registry entry added")
        print("\n✓ Font installed successfully!")
        print("\nNOTE: You may need to restart the application for icons to appear.")
        return True

    except PermissionError:
        print("\n✗ Permission denied. Please run as Administrator.")
        print("   Right-click Command Prompt > 'Run as administrator'")
        print("   Then run: python install_material_icons.py")
        return False
    except Exception as e:
        print(f"\n✗ Installation failed: {e}")
        print("\nAlternative: Double-click the downloaded font file and click 'Install'")
        print(f"Font location: {font_path}")
        return False


def main():
    """Main installation function"""
    print("="*60)
    print("Google Material Symbols Font Installer")
    print("For ClutchG Application")
    print("="*60 + "\n")

    if not is_windows():
        print("This installer is designed for Windows.")
        print("\nFor other platforms, please visit:")
        print("https://fonts.google.com/icons")
        choice = input("\nOpen download page in browser? (y/n): ").strip().lower()
        if choice in ('y', 'yes'):
            import webbrowser
            webbrowser.open("https://fonts.google.com/icons")
        return

    try:
        # Download font
        font_path = download_material_symbols()

        # Install font
        success = install_font_on_windows(font_path)

        if success:
            # Clean up downloaded file
            try:
                font_path.unlink()
                print(f"✓ Cleaned up temporary file")
            except:
                pass

            print("\n" + "="*60)
            print("Installation Complete!")
            print("="*60)
            print("\nNext steps:")
            print("1. Restart ClutchG application")
            print("2. Icons should now display correctly")
            print("="*60)

    except Exception as e:
        print(f"\n✗ Installation failed: {e}")
        print("\nPlease install manually:")
        print("1. Visit: https://fonts.google.com/icons")
        print("2. Click 'Download family'")
        print("3. Install the .ttf files")


if __name__ == "__main__":
    main()
