"""
Font Installer Helper for Tabler Icons

Checks if Tabler Icons font is installed and provides installation instructions.
The font is bundled with the application as tabler-icons.ttf — this module
is a fallback for verifying the font loaded correctly.

Fonts are loaded via Windows GDI API (AddFontResourceEx) in font_loader.py.
"""

import platform
import webbrowser


def check_tabler_icons_installed() -> bool:
    """
    Check if Tabler Icons font is installed/loaded.

    Returns:
        True if font is available, False otherwise
    """
    try:
        import tkinter as tk
        import tkinter.font as tkfont

        root = getattr(tk, "_default_root", None)
        if root is None:
            return False
        return "Tabler Icons" in tkfont.families(root)
    except Exception:
        return False


def tabler_icons_instructions() -> str:
    """
    Get instructions for Tabler Icons font (bundled — should not normally be needed).

    Returns:
        Instructions string
    """
    return """
Tabler Icons font (tabler-icons.ttf) is bundled with ClutchG.
If icons are not displaying correctly, try the following:

1. Ensure the application files are intact (re-download if needed).
2. The font file is located at: clutchg/src/fonts/tabler-icons.ttf
3. Fonts are loaded via Windows GDI API — no extra packages needed.

For manual installation (fallback):
- Download tabler-icons.ttf from: https://github.com/tabler/tabler-icons/releases
  (via npm: @tabler/icons-webfont — dist/fonts/tabler-icons.ttf)
- Install the font system-wide (double-click on Windows, or copy to Fonts folder)
"""


def open_download_page():
    """Open browser to Tabler Icons releases page."""
    webbrowser.open("https://github.com/tabler/tabler-icons/releases")


def verify_and_prompt_install() -> bool:
    """
    Check if font is installed and prompt if not.

    Returns:
        True if font is available, False if user needs to install
    """
    if check_tabler_icons_installed():
        return True

    print("\n" + "=" * 60)
    print("Tabler Icons Font Not Found")
    print("=" * 60)
    print(tabler_icons_instructions())
    print("\nWould you like to open the download page in your browser?")
    print("(Tabler Icons font is required for icons to display correctly)")
    print("=" * 60 + "\n")

    response = input("Open download page? (y/n): ").strip().lower()
    if response in ("y", "yes"):
        open_download_page()
        print("\nAfter installing the font, please restart the application.\n")
        return False

    return False


# Keep backward-compat alias
check_material_symbols_installed = check_tabler_icons_installed


if __name__ == "__main__":
    if not verify_and_prompt_install():
        print("\nPlease ensure the font is installed and run this script again.")
    else:
        print("\nTabler Icons font is installed and ready to use!")
