"""
Integration Tests for ClutchG Application
Tests icon system, navigation, and backup/restore center integration
"""

import sys
import os
from pathlib import Path

import pytest

# Add src to path (does not affect CWD)
script_dir = Path(__file__).parent.absolute()
clutchg_dir = script_dir.parent.parent
src_dir = clutchg_dir / "src"

if src_dir.exists():
    sys.path.insert(0, str(src_dir))
else:
    pytest.skip(
        f"src directory not found at {src_dir} — cannot run integration tests",
        allow_module_level=True,
    )


@pytest.fixture(autouse=True, scope="module")
def _chdir_to_src():
    """Temporarily change CWD to src/ for this module's tests, then restore."""
    original_cwd = os.getcwd()
    os.chdir(str(src_dir))
    yield
    os.chdir(original_cwd)

def test_icon_provider():
    """Test IconProvider functionality"""
    print("\n[1/6] Testing IconProvider...")

    from gui.theme import get_icon_provider, ICON, ICON_FONT

    # Test get_icon_provider
    provider = get_icon_provider()
    assert provider is not None, "IconProvider should not be None"

    # Test ICON function
    backup_icon = ICON('backup')
    assert backup_icon is not None, "ICON('backup') should return a value"
    assert len(backup_icon) == 1, "Icon should be a single character"

    check_icon = ICON('check')
    assert check_icon is not None, "ICON('check') should return a value"

    # Test ICON_FONT function
    font = ICON_FONT()
    assert font is not None, "ICON_FONT() should return a tuple"
    assert isinstance(font, tuple), "ICON_FONT() should return a tuple"

    # Test fallback for nonexistent icon
    fallback_icon = ICON('nonexistent_icon')
    assert fallback_icon is not None, "ICON should have fallback for unknown icons"

    print("  [OK] IconProvider working correctly")
    print(f"  [INFO] Backup icon length: {len(backup_icon)}")
    print(f"  [INFO] Font: {font}")

def test_theme_integration():
    """Test theme.py ICON integration"""
    print("\n[2/6] Testing theme.py ICON integration...")

    from gui.theme import ICON, ICON_FONT

    # Test common icons
    icons_to_test = ['backup', 'check', 'error', 'warning', 'success', 'folder']

    for icon_name in icons_to_test:
        icon = ICON(icon_name)
        assert icon is not None, f"ICON('{icon_name}') should return a value"
        print(f"  [OK] {icon_name}: length={len(icon)}")

    # Test font
    font = ICON_FONT()
    assert font is not None, "ICON_FONT() should return a tuple"
    print(f"  [OK] Font tuple: {font}")

def test_backup_restore_center_imports():
    """Test BackupRestoreCenter imports"""
    print("\n[3/6] Testing BackupRestoreCenter imports...")

    from gui.views.backup_restore_center import BackupRestoreCenter
    assert BackupRestoreCenter is not None, "BackupRestoreCenter should be importable"
    print("  [OK] BackupRestoreCenter imported successfully")

def test_views_imports():
    """Test all modified views imports"""
    print("\n[4/6] Testing modified views imports...")

    views_to_test = [
        'gui.views.profiles_minimal',
        'gui.views.scripts_minimal',
        'gui.views.help_minimal',
        'gui.views.welcome_overlay',
        'gui.components.enhanced_sidebar'
    ]

    failed = []
    for view_name in views_to_test:
        try:
            module = __import__(view_name, fromlist=[''])
            print(f"  [OK] {view_name}")
        except ImportError as e:
            print(f"  [FAIL] {view_name}: {e}")
            failed.append(view_name)

    assert not failed, f"Failed to import: {failed}"

def test_navigation_integration():
    """Test navigation integration in app_minimal"""
    print("\n[5/6] Testing navigation integration...")

    # We can't fully instantiate the app without a GUI,
    # but we can check imports
    import app_minimal
    print("  [OK] app_minimal imported successfully")

    # Check that it has the necessary components
    assert hasattr(app_minimal, 'ClutchGApp'), "ClutchGApp class should exist"
    print("  [OK] ClutchGApp class exists")

def test_no_emojis_in_views():
    """Test that emojis have been replaced with ICON() calls"""
    print("\n[6/6] Testing emojis replacement in views...")

    views_to_check = [
        'gui/views/profiles_minimal.py',
        'gui/views/scripts_minimal.py',
        'gui/views/help_minimal.py',
        'gui/views/welcome_overlay.py'
    ]

    # Common emojis that should NOT be in the code
    forbidden_emojis = ['\\U0001F4BE', '\\U00002705', '\\U0000274C', '\\U000026A0',
                         '\\U00002139', '\\U0001F3E0', '\\U0001F4CA', '\\U000026A1',
                         '\\U0001F6E1', '\\U0001F525', '\\U0001F3AE', '\\U0001F680']

    all_clean = True

    for view_path in views_to_check:
        full_path = src_dir / view_path
        if not full_path.exists():
            print(f"  [WARN] {view_path} not found")
            continue

        content = full_path.read_text(encoding='utf-8')
        found_emojis = []

        # Check for emoji patterns
        for emoji_unicode in forbidden_emojis:
            emoji_char = bytes(emoji_unicode, 'utf-8').decode('unicode-escape')
            if emoji_char in content:
                found_emojis.append(emoji_unicode)

        if found_emojis:
            print(f"  [FAIL] {view_path}: Found emojis {found_emojis}")
            all_clean = False
        else:
            print(f"  [OK] {view_path}: No emojis found")

    assert all_clean, "Some views still contain forbidden emojis"

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("ClutchG Integration Tests")
    print("=" * 60)

    tests = [
        test_icon_provider,
        test_theme_integration,
        test_backup_restore_center_imports,
        test_views_imports,
        test_navigation_integration,
        test_no_emojis_in_views
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[FAIL] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
