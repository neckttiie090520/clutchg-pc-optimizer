"""
Font Installer Helper for Google Material Symbols
Checks if Material Symbols font is installed and provides installation instructions
"""

import platform
import subprocess
import webbrowser
from pathlib import Path


def check_material_symbols_installed() -> bool:
    """
    Check if Material Symbols Outlined font is installed

    Returns:
        True if font is available, False otherwise
    """
    try:
        import customtkinter as ctk
        import tkinter as tk

        # Try to create a font with Material Symbols
        test_font = ctk.CTkFont(family="Material Symbols Outlined", size=12)

        # Try to use it in a temporary widget
        root = tk.Tk()
        root.withdraw()  # Hide window

        label = tk.Label(root, text="\ue8b8", font=("Material Symbols Outlined", 12))
        label.update()

        # If we got here without error, font is available
        root.destroy()
        return True
    except Exception:
        return False


def install_material_symbols_instructions() -> str:
    """
    Get installation instructions for Material Symbols font

    Returns:
        Installation instructions string
    """
    system = platform.system()

    if system == "Windows":
        return """
Material Symbols Font Installation for Windows:

Method 1: Automatic (Recommended)
1. Download: https://github.com/google/material-design-icons/raw/mafont/VariableFont/MaterialSymbolsOutlined%5Bopsz,wght%5D.ttf
2. Double-click the downloaded .ttf file
3. Click "Install" button

Method 2: Manual
1. Download the font from: https://fonts.google.com/icons
2. Copy to: C:\\Windows\\Fonts
3. Or open Settings > Personalization > Fonts > Drag & drop the .ttf file

Method 3: Using Google Fonts
1. Visit: https://fonts.google.com/icons
2. Select any icon
3. Click "Download family" to get all Material Symbols fonts
"""
    elif system == "Darwin":  # macOS
        return """
Material Symbols Font Installation for macOS:

Method 1: Font Book (Recommended)
1. Download: https://github.com/google/material-design-icons/raw/mafont/VariableFont/MaterialSymbolsOutlined%5Bopsz,wght%5D.ttf
2. Double-click the downloaded .ttf file
3. Click "Install Font" in Font Book

Method 2: Manual
1. Copy .ttf file to: ~/Library/Fonts/ or /Library/Fonts/
2. Open Font Book and verify installation
"""
    else:  # Linux
        return """
Material Symbols Font Installation for Linux:

Method 1: Package Manager
Ubuntu/Debian:
  sudo apt install fonts-material-design-icons

Fedora:
  sudo dnf install google-material-design-icons

Arch:
  sudo pacman -S material-design-icons

Method 2: Manual
1. Download: https://github.com/google/material-design-icons/raw/mafont/VariableFont/MaterialSymbolsOutlined%5Bopsz,wght%5D.ttf
2. Copy to: ~/.local/share/fonts/ or /usr/share/fonts/
3. Run: fc-cache -fv
"""


def open_download_page():
    """Open browser to Material Symbols download page"""
    webbrowser.open("https://fonts.google.com/icons")


def verify_and_prompt_install() -> bool:
    """
    Check if font is installed and prompt if not

    Returns:
        True if font is available, False if user needs to install
    """
    if check_material_symbols_installed():
        return True

    # Font not installed, show instructions
    print("\n" + "="*60)
    print("Google Material Symbols Font Not Found")
    print("="*60)
    print(install_material_symbols_instructions())
    print("\nWould you like to open the download page in your browser?")
    print("(Material Symbols font is required for icons to display correctly)")
    print("="*60 + "\n")

    response = input("Open download page? (y/n): ").strip().lower()
    if response in ('y', 'yes'):
        open_download_page()
        print("\nAfter installing the font, please restart the application.\n")
        return False

    return False


if __name__ == "__main__":
    # Run as standalone script
    if not verify_and_prompt_install():
        print("\nPlease install the font and run this script again.")
    else:
        print("\n✓ Material Symbols font is installed and ready to use!")
