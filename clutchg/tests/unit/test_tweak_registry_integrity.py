"""
Unit Tests for BatchParser.validate_script — Tweak Registry Integrity

Verifies that the safety scanner correctly identifies dangerous patterns
in batch scripts and clears clean scripts. All tests use in-memory
temporary files so no real batch scripts are executed.
"""

import pytest
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.batch_parser import BatchParser, BatchScript, CATEGORY_META


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_script(tmp_path: Path, content: str, name: str = "test_script") -> BatchScript:
    """Write *content* to a .bat file and return a minimal BatchScript."""
    bat_file = tmp_path / f"{name}.bat"
    bat_file.write_text(content, encoding='utf-8')
    return BatchScript(
        path=bat_file,
        name=name,
        description="test",
        category="registry",
        requires_admin=True,
        estimated_time=15,
        requires_restart=False,
        risk_level="MEDIUM",
        tags=["registry"],
    )


def _make_parser(tmp_path: Path) -> BatchParser:
    return BatchParser(tmp_path)


# ---------------------------------------------------------------------------
# Safe scripts pass validation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidateScriptSafe:

    def test_empty_script_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        script = _make_script(tmp_path, "@echo off\n")
        assert parser.validate_script(script) is True

    def test_simple_reg_add_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        content = (
            "@echo off\n"
            "reg add \"HKLM\\SOFTWARE\\Policies\" /v TestValue /t REG_DWORD /d 1 /f\n"
        )
        script = _make_script(tmp_path, content)
        assert parser.validate_script(script) is True

    def test_service_config_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        content = (
            "@echo off\n"
            "sc config SysMain start= disabled\n"
            "net stop SysMain\n"
        )
        script = _make_script(tmp_path, content)
        assert parser.validate_script(script) is True

    def test_bcdedit_set_passes(self, tmp_path):
        """bcdedit /set is safe; only /delete and /deletevalue are blocked."""
        parser = _make_parser(tmp_path)
        content = "@echo off\nbcdedit /set useplatformtick yes\n"
        script = _make_script(tmp_path, content)
        assert parser.validate_script(script) is True

    def test_comments_only_passes(self, tmp_path):
        parser = _make_parser(tmp_path)
        content = ":: This script does nothing dangerous\n@echo off\necho Done\n"
        script = _make_script(tmp_path, content)
        assert parser.validate_script(script) is True

    def test_missing_file_returns_false(self, tmp_path):
        parser = _make_parser(tmp_path)
        ghost = BatchScript(
            path=tmp_path / "nonexistent.bat",
            name="ghost",
            description="",
            category="other",
            requires_admin=False,
            estimated_time=0,
            requires_restart=False,
            risk_level="LOW",
        )
        assert parser.validate_script(ghost) is False


# ---------------------------------------------------------------------------
# Dangerous patterns are blocked
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidateScriptDangerousPatterns:

    DANGEROUS_CASES = [
        ("format c:", "@echo off\nformat c: /q\n"),
        ("format d:", "@echo off\nformat d: /q\n"),
        ("format e:", "@echo off\nformat e: /q\n"),
        ("format f:", "@echo off\nformat f: /q\n"),
        ("del windows", "@echo off\ndel /s /q c:\\windows\n"),
        ("del root", "@echo off\ndel /f /s /q c:\\\n"),
        ("rd windows", "@echo off\nrd /s /q c:\\windows\n"),
        ("rd root", "@echo off\nrd /s /q c:\\\n"),
        ("rmdir windows", "@echo off\nrmdir /s /q c:\\windows\n"),
        ("rmdir root", "@echo off\nrmdir /s /q c:\\\n"),
        ("diskpart", "@echo off\ndiskpart\n"),
        ("bcdedit /deletevalue", "@echo off\nbcdedit /deletevalue {current} nx\n"),
        ("bcdedit /delete", "@echo off\nbcdedit /delete {badmemory}\n"),
        ("cipher /w:", "@echo off\ncipher /w:c:\\\n"),
        ("reg delete", "@echo off\nreg delete HKLM\\SOFTWARE\\Test /f\n"),
        ("remove-item -recurse", "@echo off\npowershell Remove-Item -Recurse C:\\Temp\n"),
        ("remove-item -force", "@echo off\npowershell Remove-Item -Force C:\\Foo\n"),
        ("shutdown /s", "@echo off\nshutdown /s /t 0\n"),
        ("shutdown /r", "@echo off\nshutdown /r /t 0\n"),
        ("shutdown /p", "@echo off\nshutdown /p\n"),
        ("shutdown /h", "@echo off\nshutdown /h\n"),
        ("taskkill csrss", "@echo off\ntaskkill /f /im csrss.exe\n"),
        ("taskkill svchost", "@echo off\ntaskkill /f /im svchost.exe\n"),
        ("taskkill lsass", "@echo off\ntaskkill /f /im lsass.exe\n"),
        ("taskkill winlogon", "@echo off\ntaskkill /f /im winlogon.exe\n"),
        ("takeown windows", "@echo off\ntakeown /f c:\\windows /r\n"),
        ("icacls windows", "@echo off\nicacls c:\\windows /grant everyone:F\n"),
    ]

    @pytest.mark.parametrize("label,content", DANGEROUS_CASES)
    def test_dangerous_pattern_blocked(self, tmp_path, label, content):
        parser = _make_parser(tmp_path)
        # Build a safe filename: keep only alphanumerics and underscores
        safe_label = "".join(c if c.isalnum() else "_" for c in label[:20])
        script = _make_script(tmp_path, content, name=f"dangerous_{safe_label}")
        assert parser.validate_script(script) is False, (
            f"Expected '{label}' to be blocked but validate_script returned True"
        )

    def test_case_insensitive_blocking(self, tmp_path):
        """Dangerous patterns should be caught regardless of case."""
        parser = _make_parser(tmp_path)
        content = "@echo off\nFORMAT C:\n"
        script = _make_script(tmp_path, content, name="upper_case")
        assert parser.validate_script(script) is False

    def test_mixed_case_diskpart(self, tmp_path):
        parser = _make_parser(tmp_path)
        content = "@echo off\nDiskPart\n"
        script = _make_script(tmp_path, content, name="mixed_diskpart")
        assert parser.validate_script(script) is False


# ---------------------------------------------------------------------------
# CATEGORY_META integrity
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCategoryMeta:

    REQUIRED_KEYS = {"icon", "color", "dim", "label"}
    KNOWN_CATEGORIES = [
        "power", "bcdedit", "services", "network", "registry",
        "gpu", "storage", "maintenance", "system", "profile",
        "backup", "safety", "validation", "logging", "other",
    ]

    def test_all_known_categories_present(self):
        for cat in self.KNOWN_CATEGORIES:
            assert cat in CATEGORY_META, f"Missing category in CATEGORY_META: {cat}"

    def test_each_category_has_required_keys(self):
        for cat, meta in CATEGORY_META.items():
            missing = self.REQUIRED_KEYS - set(meta.keys())
            assert not missing, f"Category '{cat}' missing keys: {missing}"

    def test_get_category_meta_returns_dict(self):
        meta = BatchParser.get_category_meta("registry")
        assert isinstance(meta, dict)
        assert "color" in meta

    def test_get_category_meta_unknown_returns_other(self):
        meta = BatchParser.get_category_meta("does_not_exist")
        assert meta == CATEGORY_META["other"]

    def test_get_all_categories_returns_all_keys(self):
        cats = BatchParser.get_all_categories()
        assert set(cats) == set(CATEGORY_META.keys())


# ---------------------------------------------------------------------------
# _determine_category
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDetermineCategory:

    def _cat(self, tmp_path: Path, subdir: str, filename: str) -> str:
        """Build a fake path and resolve its category."""
        fake_path = tmp_path / subdir / f"{filename}.bat"
        fake_path.parent.mkdir(parents=True, exist_ok=True)
        fake_path.touch()
        parser = _make_parser(tmp_path)
        return parser._determine_category(fake_path)

    def test_profiles_directory(self, tmp_path):
        assert self._cat(tmp_path, "profiles", "safe-profile") == "profile"

    def test_backup_directory(self, tmp_path):
        assert self._cat(tmp_path, "backup", "create-restore-point") == "backup"

    def test_safety_directory(self, tmp_path):
        assert self._cat(tmp_path, "safety", "admin-check") == "safety"

    def test_core_power(self, tmp_path):
        assert self._cat(tmp_path, "core", "power-settings") == "power"

    def test_core_bcdedit(self, tmp_path):
        assert self._cat(tmp_path, "core", "bcdedit-tweaks") == "bcdedit"

    def test_core_services(self, tmp_path):
        assert self._cat(tmp_path, "core", "service-manager") == "services"

    def test_core_network(self, tmp_path):
        assert self._cat(tmp_path, "core", "network-optimize") == "network"

    def test_core_registry(self, tmp_path):
        assert self._cat(tmp_path, "core", "registry-tweaks") == "registry"

    def test_core_gpu(self, tmp_path):
        assert self._cat(tmp_path, "core", "gpu-settings") == "gpu"

    def test_core_storage(self, tmp_path):
        assert self._cat(tmp_path, "core", "storage-optimize") == "storage"

    def test_core_maintenance(self, tmp_path):
        assert self._cat(tmp_path, "core", "maintenance-tasks") == "maintenance"

    def test_core_unknown_defaults_to_other(self, tmp_path):
        assert self._cat(tmp_path, "core", "mystery-script") == "other"


# ---------------------------------------------------------------------------
# _determine_risk_level
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDetermineRiskLevel:

    def _risk(self, tmp_path: Path, category: str, filename: str) -> str:
        fake_path = tmp_path / f"{filename}.bat"
        fake_path.touch()
        parser = _make_parser(tmp_path)
        return parser._determine_risk_level(category, fake_path)

    def test_backup_is_low(self, tmp_path):
        assert self._risk(tmp_path, "backup", "create-backup") == "LOW"

    def test_safety_is_low(self, tmp_path):
        assert self._risk(tmp_path, "safety", "admin-check") == "LOW"

    def test_bcdedit_is_high(self, tmp_path):
        assert self._risk(tmp_path, "bcdedit", "bcdedit-tweaks") == "HIGH"

    def test_services_is_high(self, tmp_path):
        assert self._risk(tmp_path, "services", "service-manager") == "HIGH"

    def test_power_is_medium(self, tmp_path):
        assert self._risk(tmp_path, "power", "power-settings") == "MEDIUM"

    def test_registry_is_medium(self, tmp_path):
        assert self._risk(tmp_path, "registry", "registry-tweaks") == "MEDIUM"

    def test_profile_extreme_is_high(self, tmp_path):
        assert self._risk(tmp_path, "profile", "extreme-profile") == "HIGH"

    def test_profile_competitive_is_medium(self, tmp_path):
        assert self._risk(tmp_path, "profile", "competitive-profile") == "MEDIUM"

    def test_profile_safe_is_low(self, tmp_path):
        assert self._risk(tmp_path, "profile", "safe-profile") == "LOW"
