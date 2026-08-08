"""Static safety contracts for batch profile loading and application.

These tests read batch files as text and never execute CMD or mutate Windows.
"""

from pathlib import Path
import re

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
OPTIMIZER = REPO_ROOT / "src" / "optimizer.bat"
PROFILES = REPO_ROOT / "src" / "profiles"
SYSTEM_DETECT = REPO_ROOT / "src" / "core" / "system-detect.bat"
STORAGE_OPTIMIZER = REPO_ROOT / "src" / "core" / "storage-optimizer.bat"
POWER_MANAGER_ENHANCED = REPO_ROOT / "src" / "core" / "power-manager-enhanced.bat"
PROFILE_FILES = tuple(PROFILES / name for name in (
    "safe-profile.bat",
    "competitive-profile.bat",
    "extreme-profile.bat",
))

PROFILE_FLAGS = (
    "TWEAK_POWER",
    "TWEAK_BCDEDIT_SAFE",
    "TWEAK_BCDEDIT_ADVANCED",
    "TWEAK_SERVICES",
    "TWEAK_TELEMETRY",
    "TWEAK_GAMING",
    "TWEAK_VISUAL",
    "TWEAK_NETWORK_SAFE",
    "TWEAK_NETWORK_AGGRESSIVE",
    "TWEAK_NETWORK",
    "TWEAK_GPU",
    "TWEAK_POWER_ENHANCED",
    "TWEAK_GPU_ENHANCED",
    "TWEAK_KERNEL_INPUT",
    "TWEAK_STORAGE",
    "TWEAK_MAINTENANCE",
    "TWEAK_BENCHMARK",
    "TWEAK_TELEMETRY_FULL",
    "TWEAK_INPUT",
    "TWEAK_DEBLOAT",
    "TWEAK_NETWORK_TCP",
)

MUTATION_PATTERNS = (
    r"^\s*reg\s+(?:add|delete|import)\b",
    r"^\s*(?:powercfg|bcdedit|netsh|fsutil)\b",
    r"^\s*sc\s+config\b",
    r"^\s*net\s+(?:start|stop)\b",
    r"^\s*powershell\b",
    r"^\s*call\s+.*(?:core|safety|backup).*\.bat",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.mark.unit
class TestDeclarativeProfiles:
    @pytest.mark.parametrize("profile_path", PROFILE_FILES)
    def test_profile_sets_every_flag_exactly_once(self, profile_path):
        content = _read(profile_path)
        for flag in PROFILE_FLAGS:
            assert len(re.findall(rf'^set "{flag}=[01]"$', content, re.MULTILINE)) == 1
        declared = set(re.findall(r'^set "(TWEAK_[A-Z0-9_]+)=[01]"$', content, re.MULTILINE))
        assert declared == set(PROFILE_FLAGS)

    @pytest.mark.parametrize("profile_path", PROFILE_FILES)
    def test_profile_contains_no_system_mutation(self, profile_path):
        content = _read(profile_path)
        for pattern in MUTATION_PATTERNS:
            assert re.search(pattern, content, re.IGNORECASE | re.MULTILINE) is None

    @pytest.mark.parametrize("profile_path", PROFILE_FILES)
    def test_default_profiles_exclude_irreversible_and_security_reducing_actions(self, profile_path):
        content = _read(profile_path)
        for flag in (
            "TWEAK_DEBLOAT",
            "TWEAK_BCDEDIT_ADVANCED",
        ):
            assert f'set "{flag}=0"' in content

    def test_profile_payloads_are_exact_and_distinct(self):
        expected = {
            "safe-profile.bat": {"TWEAK_POWER"},
            "competitive-profile.bat": {"TWEAK_POWER", "TWEAK_SERVICES"},
            "extreme-profile.bat": {
                "TWEAK_POWER",
                "TWEAK_BCDEDIT_SAFE",
                "TWEAK_SERVICES",
            },
        }
        actual = {}
        for filename, enabled_expected in expected.items():
            content = _read(PROFILES / filename)
            enabled = set(
                re.findall(r'^set "(TWEAK_[A-Z0-9_]+)=1"$', content, re.MULTILINE)
            )
            assert enabled == enabled_expected
            actual[filename] = enabled

        assert len({frozenset(flags) for flags in actual.values()}) == len(actual)


@pytest.mark.unit
class TestOptimizerProfileGates:
    def test_optimizer_resets_all_flags_before_each_profile_load(self):
        content = _read(OPTIMIZER)
        assert "\n:reset_profile_flags\n" in content
        for flag in PROFILE_FLAGS:
            assert f'set "{flag}=0"' in content
        for label in ("profile_safe", "profile_competitive", "profile_extreme"):
            block = content.split(f"\n:{label}\n", 1)[1].split("\n:", 1)[0]
            assert "call :reset_profile_flags" in block
            assert "if errorlevel 1" in block

    def test_recovery_gates_precede_any_tweak_module(self):
        content = _read(OPTIMIZER)
        apply_block = content.split(":apply_profile\n", 1)[1].split("\n:: ============================================\n:: Custom Menu", 1)[0]
        restore_pos = apply_block.index('restore-point.bat" create_restore_point')
        backup_pos = apply_block.index('flight-recorder.bat" create_snapshot')
        first_module_pos = apply_block.index("call :run_tweak_module")
        assert restore_pos < first_module_pos
        assert backup_pos < first_module_pos
        assert 'if not "!CLUTCHG_BACKUP_READY!"=="1"' in apply_block

    def test_profile_application_uses_fail_fast_module_wrapper(self):
        content = _read(OPTIMIZER)
        assert "\n:run_tweak_module\n" in content
        assert 'if not "!MODULE_CODE!"=="0"' in content
        assert "exit /b !MODULE_CODE!" in content
