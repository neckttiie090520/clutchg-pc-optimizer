"""
Coverage Expansion Tests — Phase 3

New unit tests covering gaps identified in the audit:
- config.py: load/save/reset/defaults
- theme.py: ThemeManager, get_colors, get_score_color, get_risk_colors
- batch_parser.py: validate_script edge cases (end-of-line, mixed-case, malformed)
- tweak_registry.py: get_tweaks_for_preset, field integrity
- profile_manager.py: invalid profile, export/import preset
- localization: UI_STRINGS key parity between EN/TH
- security: bcdedit /deletevalue allowed (safe rollback)
"""

import json
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# ============================================================================
# CONFIG TESTS
# ============================================================================

@pytest.mark.unit
class TestConfigManager:

    def test_load_returns_dict_with_defaults(self, tmp_path):
        from core.config import ConfigManager
        cm = ConfigManager(tmp_path)
        config = cm.load_config()
        assert isinstance(config, dict)
        assert "language" in config
        assert "auto_backup" in config
        assert "confirm_actions" in config

    def test_default_config_has_required_keys(self, tmp_path):
        from core.config import ConfigManager
        cm = ConfigManager(tmp_path)
        defaults = cm.get_default_config()
        required = {"version", "language", "auto_backup", "confirm_actions",
                    "log_level", "batch_scripts_dir", "backup_dir", "max_backups",
                    "default_profile"}
        for key in required:
            assert key in defaults, f"Missing default key: {key}"

    def test_save_and_reload_round_trip(self, tmp_path):
        from core.config import ConfigManager
        cm = ConfigManager(tmp_path)
        config = cm.load_config()
        config["language"] = "th"
        config["auto_backup"] = False
        assert cm.save_config(config) is True

        cm2 = ConfigManager(tmp_path)
        reloaded = cm2.load_config()
        assert reloaded["language"] == "th"
        assert reloaded["auto_backup"] is False

    def test_save_creates_user_config_file(self, tmp_path):
        from core.config import ConfigManager
        cm = ConfigManager(tmp_path)
        cm.save_config({"language": "en"})
        assert (tmp_path / "user_config.json").exists()

    def test_reset_to_defaults_removes_user_config(self, tmp_path):
        from core.config import ConfigManager
        cm = ConfigManager(tmp_path)
        cm.save_config({"language": "th"})
        assert (tmp_path / "user_config.json").exists()
        defaults = cm.reset_to_defaults()
        assert not (tmp_path / "user_config.json").exists()
        assert defaults["language"] == "en"

    def test_load_with_corrupt_user_config_falls_back_to_defaults(self, tmp_path):
        from core.config import ConfigManager
        (tmp_path / "user_config.json").write_text("NOT VALID JSON", encoding="utf-8")
        cm = ConfigManager(tmp_path)
        config = cm.load_config()
        assert isinstance(config, dict)
        assert "language" in config

    def test_load_with_missing_directory_creates_it(self, tmp_path):
        from core.config import ConfigManager
        new_dir = tmp_path / "nested" / "config"
        cm = ConfigManager(new_dir)
        assert new_dir.exists()
        config = cm.load_config()
        assert isinstance(config, dict)

    def test_save_returns_false_on_permission_error(self, tmp_path, monkeypatch):
        from core.config import ConfigManager
        import builtins
        cm = ConfigManager(tmp_path)

        def bad_open(*args, **kwargs):
            raise PermissionError("no write access")

        monkeypatch.setattr(builtins, "open", bad_open)
        result = cm.save_config({"language": "en"})
        assert result is False


# ============================================================================
# BATCH PARSER — VALIDATE_SCRIPT EDGE CASES
# ============================================================================

def _make_parser(tmp_path):
    from core.batch_parser import BatchParser
    return BatchParser(tmp_path)


def _make_script(tmp_path, content: str, name: str = "test_script.bat"):
    """Write a .bat file and wrap it in a BatchScript object."""
    from core.batch_parser import BatchScript
    p = tmp_path / name
    if content:
        p.write_text(content, encoding="utf-8")
    else:
        p.touch()
    return BatchScript(
        path=p,
        name=name,
        description="test",
        category="other",
        requires_admin=False,
        estimated_time=1,
        requires_restart=False,
        risk_level="LOW",
    )


def _make_missing_script(tmp_path, name: str = "missing.bat"):
    """Return a BatchScript whose path does not exist."""
    from core.batch_parser import BatchScript
    return BatchScript(
        path=tmp_path / name,
        name=name,
        description="test",
        category="other",
        requires_admin=False,
        estimated_time=1,
        requires_restart=False,
        risk_level="LOW",
    )


@pytest.mark.unit
class TestValidateScriptEdgeCases:

    def test_valid_script_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\necho Hello World\n")
        assert parser.validate_script(script) is True

    def test_dangerous_pattern_at_end_of_line_no_trailing_space(self, tmp_path):
        """shutdown /p at end-of-line (no trailing space) must be blocked."""
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nshutdown /p\n")
        assert parser.validate_script(script) is False

    def test_shutdown_h_at_end_of_line(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nshutdown /h\n")
        assert parser.validate_script(script) is False

    def test_shutdown_s_with_args(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nshutdown /s /t 0\n")
        assert parser.validate_script(script) is False

    def test_shutdown_r_with_args(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nshutdown /r /t 30\n")
        assert parser.validate_script(script) is False

    def test_mixed_case_format_blocked(self, tmp_path):
        """Pattern detection must be case-insensitive."""
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nFORMAT C: /q\n")
        assert parser.validate_script(script) is False

    def test_mixed_case_diskpart_blocked(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nDISKPART\n")
        assert parser.validate_script(script) is False

    def test_bcdedit_deletevalue_is_allowed(self, tmp_path):
        """bcdedit /deletevalue is a safe rollback operation and must NOT be blocked."""
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nbcdedit /deletevalue {current} nx\n")
        assert parser.validate_script(script) is True

    def test_bcdedit_delete_entry_is_blocked(self, tmp_path):
        """bcdedit /delete (full entry removal) must be blocked."""
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\nbcdedit /delete {badmemory}\n")
        assert parser.validate_script(script) is False

    def test_empty_script_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "")
        assert parser.validate_script(script) is True

    def test_nonexistent_script_fails(self, tmp_path):
        parser = _make_parser(tmp_path)
        missing = _make_missing_script(tmp_path)
        assert parser.validate_script(missing) is False

    def test_valid_registry_tweak_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        content = "@echo off\nreg add HKLM\\SYSTEM\\CurrentControlSet\\Control /v FooBar /t REG_DWORD /d 1 /f\n"
        script = _make_script(tmp_path, content)
        assert parser.validate_script(script) is True


# ============================================================================
# THEME TESTS (headless-safe — no CTk window needed)
# ============================================================================

@pytest.mark.unit
class TestThemeManager:

    def test_get_colors_returns_dict(self):
        from gui.theme import theme_manager
        colors = theme_manager.get_colors()
        assert isinstance(colors, dict)

    def test_get_colors_has_required_keys(self):
        from gui.theme import theme_manager
        colors = theme_manager.get_colors()
        required = {
            "bg_primary", "bg_secondary", "bg_card", "bg_elevated", "bg_hover",
            "text_primary", "text_secondary", "text_muted",
            "accent", "accent_hover",
            "border", "border_subtle",
        }
        for key in required:
            assert key in colors, f"Missing theme color key: {key}"

    def test_get_colors_values_are_strings(self):
        from gui.theme import theme_manager
        colors = theme_manager.get_colors()
        for k, v in colors.items():
            if not k.startswith("glass"):
                assert isinstance(v, str), f"Color '{k}' value is not a string: {v!r}"

    def test_current_theme_is_set(self):
        from gui.theme import theme_manager
        assert theme_manager.current_theme in {"dark", "zinc", "light", "modern"}

    def test_current_accent_is_set(self):
        from gui.theme import theme_manager
        assert isinstance(theme_manager.current_accent, str)
        assert len(theme_manager.current_accent) > 0

    def test_get_score_color_excellent(self):
        from gui.theme import get_score_color
        color = get_score_color(85)
        assert isinstance(color, str)
        assert color.startswith("#")

    def test_get_score_color_good(self):
        from gui.theme import get_score_color
        color = get_score_color(65)
        assert isinstance(color, str)

    def test_get_score_color_average(self):
        from gui.theme import get_score_color
        color = get_score_color(45)
        assert isinstance(color, str)

    def test_get_score_color_low(self):
        from gui.theme import get_score_color
        color = get_score_color(20)
        assert isinstance(color, str)

    def test_get_risk_colors_low(self):
        from gui.theme import get_risk_colors
        result = get_risk_colors("LOW")
        assert "primary" in result
        assert "dim" in result

    def test_get_risk_colors_medium(self):
        from gui.theme import get_risk_colors
        result = get_risk_colors("MEDIUM")
        assert "primary" in result

    def test_get_risk_colors_high(self):
        from gui.theme import get_risk_colors
        result = get_risk_colors("HIGH")
        assert "primary" in result

    def test_get_risk_colors_unknown(self):
        from gui.theme import get_risk_colors
        result = get_risk_colors("UNKNOWN")
        assert "primary" in result

    def test_icon_function_returns_single_char(self):
        from gui.theme import ICON
        icon = ICON("backup")
        assert isinstance(icon, str)
        assert len(icon) == 1

    def test_icon_function_fallback_for_unknown(self):
        from gui.theme import ICON
        icon = ICON("nonexistent_icon_xyz")
        assert isinstance(icon, str)  # Returns empty string as fallback, never raises

    def test_icon_font_returns_tuple(self):
        from gui.theme import ICON_FONT
        font = ICON_FONT()
        assert isinstance(font, tuple)
        assert len(font) >= 1
        assert isinstance(font[0], str)


# ============================================================================
# TWEAK REGISTRY INTEGRITY
# ============================================================================

@pytest.mark.unit
class TestTweakRegistryFields:

    def _get_registry(self):
        from core.tweak_registry import TweakRegistry
        return TweakRegistry()

    def test_registry_loads_without_error(self):
        reg = self._get_registry()
        assert reg is not None

    def test_get_tweaks_for_safe_profile(self):
        reg = self._get_registry()
        tweaks = reg.get_tweaks_for_preset("SAFE")
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0

    def test_get_tweaks_for_competitive_profile(self):
        reg = self._get_registry()
        tweaks = reg.get_tweaks_for_preset("COMPETITIVE")
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0

    def test_get_tweaks_for_extreme_profile(self):
        reg = self._get_registry()
        tweaks = reg.get_tweaks_for_preset("EXTREME")
        assert isinstance(tweaks, list)
        assert len(tweaks) > 0

    def test_safe_subset_of_competitive(self):
        """SAFE tweaks should be a subset of COMPETITIVE tweaks (by id)."""
        reg = self._get_registry()
        safe_ids = {t.id for t in reg.get_tweaks_for_preset("SAFE")}
        comp_ids = {t.id for t in reg.get_tweaks_for_preset("COMPETITIVE")}
        assert safe_ids.issubset(comp_ids), (
            f"SAFE tweaks not a subset of COMPETITIVE: {safe_ids - comp_ids}"
        )

    def test_all_tweaks_have_required_fields(self):
        reg = self._get_registry()
        all_tweaks = reg.get_all_tweaks()
        required = {"id", "name", "description", "risk_level",
                    "preset_safe", "preset_competitive", "preset_extreme"}
        for tweak in all_tweaks:
            for field in required:
                assert hasattr(tweak, field), f"Tweak missing field: {field}"
                val = getattr(tweak, field)
                assert val is not None, f"Tweak '{tweak.id}' has None for '{field}'"

    def test_all_risk_levels_valid(self):
        reg = self._get_registry()
        valid_levels = {"LOW", "MEDIUM", "HIGH"}
        for tweak in reg.get_all_tweaks():
            assert tweak.risk_level in valid_levels, (
                f"Tweak '{tweak.id}' has invalid risk_level: {tweak.risk_level!r}"
            )

    def test_no_forbidden_patterns_in_tweaks(self):
        """No tweak should contain hardcoded dangerous operations."""
        reg = self._get_registry()
        forbidden = {"format c:", "diskpart", "shutdown /p", "shutdown /h"}
        for tweak in reg.get_all_tweaks():
            if hasattr(tweak, "command") and tweak.command:
                cmd_lower = tweak.command.lower()
                for f in forbidden:
                    assert f not in cmd_lower, (
                        f"Tweak '{tweak.id}' contains forbidden pattern: {f!r}"
                    )


# ============================================================================
# LOCALIZATION — UI_STRINGS KEY PARITY
# ============================================================================

@pytest.mark.unit
class TestLocalizationKeyParity:
    """Verify EN and TH UI_STRINGS have identical keys in every view."""

    def _get_ui_strings(self, module_path: str, class_name: str) -> dict:
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return getattr(cls, "UI_STRINGS", {})

    def _assert_key_parity(self, ui_strings: dict, source: str):
        if "en" not in ui_strings or "th" not in ui_strings:
            return
        en_keys = set(ui_strings["en"].keys())
        th_keys = set(ui_strings["th"].keys())
        missing_in_th = en_keys - th_keys
        extra_in_th = th_keys - en_keys
        assert not missing_in_th, f"{source}: TH missing keys: {missing_in_th}"
        assert not extra_in_th, f"{source}: TH has extra keys: {extra_in_th}"

    def test_settings_view_key_parity(self):
        ui = self._get_ui_strings("gui.views.settings_minimal", "SettingsView")
        self._assert_key_parity(ui, "SettingsView")

    def test_help_view_key_parity(self):
        ui = self._get_ui_strings("gui.views.help_minimal", "HelpView")
        self._assert_key_parity(ui, "HelpView")

    def test_profiles_view_key_parity(self):
        ui = self._get_ui_strings("gui.views.profiles_minimal", "ProfilesView")
        self._assert_key_parity(ui, "ProfilesView")

    def test_scripts_view_key_parity(self):
        ui = self._get_ui_strings("gui.views.scripts_minimal", "ScriptsView")
        self._assert_key_parity(ui, "ScriptsView")

    def test_backup_restore_center_key_parity(self):
        ui = self._get_ui_strings("gui.views.backup_restore_center", "BackupRestoreCenter")
        self._assert_key_parity(ui, "BackupRestoreCenter")

    def test_all_ui_strings_values_are_strings(self):
        """No UI string value should be None or non-string."""
        import importlib
        views = [
            ("gui.views.settings_minimal", "SettingsView"),
            ("gui.views.help_minimal", "HelpView"),
            ("gui.views.profiles_minimal", "ProfilesView"),
            ("gui.views.scripts_minimal", "ScriptsView"),
        ]
        for module_path, class_name in views:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            ui_strings = getattr(cls, "UI_STRINGS", {})
            for lang, strings in ui_strings.items():
                for key, val in strings.items():
                    assert isinstance(val, str), (
                        f"{class_name}[{lang}][{key}] is not a string: {val!r}"
                    )


# ============================================================================
# SECURITY TESTS
# ============================================================================

_BLOCKED = [
    ("format_c", "@echo off\nformat c: /q\n"),
    ("format_d", "@echo off\nformat d: /q\n"),
    ("diskpart", "@echo off\ndiskpart\n"),
    ("bcdedit_delete_entry", "@echo off\nbcdedit /delete {badmemory}\n"),
    ("cipher_wipe", "@echo off\ncipher /w:c:\\\n"),
    ("reg_delete", "@echo off\nreg delete HKLM\\SOFTWARE\\Test /f\n"),
    ("del_windows", "@echo off\ndel /s /q c:\\windows\n"),
    ("rd_windows", "@echo off\nrd /s /q c:\\windows\n"),
    ("removei_recurse", "@echo off\npowershell Remove-Item -Recurse C:\\Temp\n"),
    ("removei_force", "@echo off\npowershell Remove-Item -Force C:\\Foo\n"),
    ("shutdown_s", "@echo off\nshutdown /s /t 0\n"),
    ("shutdown_r", "@echo off\nshutdown /r /t 30\n"),
    ("shutdown_p", "@echo off\nshutdown /p\n"),
    ("shutdown_h", "@echo off\nshutdown /h\n"),
    ("taskkill_csrss", "@echo off\ntaskkill /f /im csrss.exe\n"),
    ("taskkill_lsass", "@echo off\ntaskkill /f /im lsass.exe\n"),
    ("takeown_windows", "@echo off\ntakeown /f c:\\windows /r\n"),
    ("icacls_windows", "@echo off\nicacls c:\\windows /grant everyone:F\n"),
]

_ALLOWED = [
    ("bcdedit_deletevalue", "@echo off\nbcdedit /deletevalue {current} nx\n"),
    ("reg_add_safe", "@echo off\nreg add HKLM\\SYSTEM\\CurrentControlSet\\Control /v T /t REG_DWORD /d 1 /f\n"),
    ("echo_hello", "@echo off\necho Hello\n"),
    ("empty_script", ""),
]


@pytest.mark.unit
class TestSecurityPatterns:
    """Verify that dangerous patterns are correctly blocked/allowed."""

    @pytest.mark.parametrize("label,content", _BLOCKED)
    def test_blocked_pattern(self, tmp_path, label, content):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, content, name=f"b_{label}.bat")
        assert parser.validate_script(script) is False, f"Expected '{label}' to be blocked"

    @pytest.mark.parametrize("label,content", _ALLOWED)
    def test_allowed_pattern(self, tmp_path, label, content):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, content, name=f"a_{label}.bat")
        assert parser.validate_script(script) is True, f"Expected '{label}' to be allowed"

    def test_case_insensitive_blocking_format(self, tmp_path):
        parser = _make_parser(tmp_path)
        cases = [
            ("ci_fmt1", "FORMAT C: /q"),
            ("ci_fmt2", "Format C: /q"),
            ("ci_fmt3", "format C: /q"),
            ("ci_fmt4", "FORMAT c: /q"),
        ]
        for safe_name, cmd in cases:
            script = _make_script(tmp_path, f"@echo off\n{cmd}\n", name=f"{safe_name}.bat")
            assert parser.validate_script(script) is False, f"'{cmd}' should be blocked"

    def test_case_insensitive_blocking_diskpart(self, tmp_path):
        parser = _make_parser(tmp_path)
        cases = [
            ("ci_dp1", "DISKPART"),
            ("ci_dp2", "DiskPart"),
            ("ci_dp3", "diskpart"),
        ]
        for safe_name, cmd in cases:
            script = _make_script(tmp_path, f"@echo off\n{cmd}\n", name=f"{safe_name}.bat")
            assert parser.validate_script(script) is False, f"'{cmd}' should be blocked"
