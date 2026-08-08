"""Failure-propagation contracts for mutating batch modules.

Static tests inspect scripts as text. The optional CMD test shadows BCDEdit with a
failing stub and therefore never changes the real boot configuration.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
CORE = REPO_ROOT / "src" / "core"

MODULE_ROUTES = {
    "service-manager.bat": (
        "apply_service_tweaks",
        "reset_all",
        "disable_service",
        "enable_service",
    ),
    "registry-utils.bat": (
        "apply_telemetry_tweaks",
        "apply_gaming_tweaks",
        "apply_visual_tweaks",
        "apply_kernel_input_tweaks",
        "reset_all",
    ),
    "telemetry-blocker.bat": (
        "apply_telemetry",
        "apply_privacy",
        "apply_ads_suggestions",
        "apply_xbox_dvr",
        "reset_all",
    ),
    "debloater.bat": (
        "apply_debloat",
        "apply_onedrive",
        "apply_copilot",
    ),
    "bcdedit-manager.bat": (
        "apply_safe_tweaks",
        "apply_advanced_tweaks",
        "reset_all",
        "export_current",
    ),
}

HELPER_LABELS = {
    "service-manager.bat": ("safe_disable", "set_manual", "reset_service"),
    "registry-utils.bat": ("reg_set", "reg_delete_if_present"),
    "telemetry-blocker.bat": (
        "reg_add",
        "reg_delete_if_present",
        "disable_optional_service",
        "enable_optional_service",
    ),
    "debloater.bat": ("remove_app", "reg_add", "reg_delete_if_present"),
    "bcdedit-manager.bat": ("bcd_set", "bcd_delete"),
}


def _read(name: str) -> str:
    return (CORE / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def _label_block(content: str, label: str) -> str:
    match = re.search(
        rf"(?ms)^:{re.escape(label)}\s*$\n(.*?)(?=^:[A-Za-z0-9_]+\s*$|\Z)",
        content,
    )
    assert match is not None, f"Missing label :{label}"
    return match.group(1)


@pytest.mark.unit
class TestPublicMutationRouteContracts:
    @pytest.mark.parametrize(
        ("module_name", "route"),
        [
            (module_name, route)
            for module_name, routes in MODULE_ROUTES.items()
            for route in routes
        ],
    )
    def test_route_initializes_and_explicitly_resolves_failure_count(
        self, module_name, route
    ):
        block = _label_block(_read(module_name), route)
        assert 'set "MODULE_FAILURES=0"' in block
        assert re.search(
            r"if\s+%MODULE_FAILURES%\s+GTR\s+0(?:\s+|\s*\([^)]*?)exit\s+/b\s+1",
            block,
            re.IGNORECASE | re.DOTALL,
        )
        assert re.search(r"(?im)^exit\s+/b\s+0\s*$", block)

    def test_telemetry_apply_all_propagates_nested_route_failures(self):
        block = _label_block(_read("telemetry-blocker.bat"), "apply_all")
        assert 'set "APPLY_ALL_FAILURES=0"' in block
        for route in (
            "apply_telemetry",
            "apply_privacy",
            "apply_ads_suggestions",
            "apply_xbox_dvr",
        ):
            call = f"call :{route}"
            assert call in block
            suffix = block.split(call, 1)[1]
            assert re.match(
                r"\s*if errorlevel 1 set /a APPLY_ALL_FAILURES\+=1",
                suffix,
                re.IGNORECASE,
            )
        assert "if %APPLY_ALL_FAILURES% GTR 0" in block
        assert re.search(r"(?im)^\s*exit\s+/b\s+1\s*$", block)


@pytest.mark.unit
class TestNestedHelperContracts:
    @pytest.mark.parametrize(
        ("module_name", "helper"),
        [
            (module_name, helper)
            for module_name, helpers in HELPER_LABELS.items()
            for helper in helpers
        ],
    )
    def test_helper_records_failures_and_returns_explicit_status(
        self, module_name, helper
    ):
        block = _label_block(_read(module_name), helper)
        assert "set /a MODULE_FAILURES+=1" in block
        assert re.search(r"(?im)^\s*exit\s+/b\s+1\s*$", block)
        assert re.search(r"(?im)^\s*exit\s+/b\s+0\s*$", block)

    @pytest.mark.parametrize(
        ("module_name", "helper"),
        (
            ("service-manager.bat", "safe_disable"),
            ("service-manager.bat", "set_manual"),
            ("service-manager.bat", "reset_service"),
            ("telemetry-blocker.bat", "disable_optional_service"),
            ("telemetry-blocker.bat", "enable_optional_service"),
        ),
    )
    def test_only_service_error_1060_is_an_absent_service_skip(
        self, module_name, helper
    ):
        block = _label_block(_read(module_name), helper)
        assert 'set "SERVICE_QUERY_CODE=%ERRORLEVEL%"' in block
        assert 'if "%SERVICE_QUERY_CODE%"=="1060"' in block
        assert "FAILED" in block
        assert "set /a MODULE_FAILURES+=1" in block


@pytest.mark.unit
class TestCommandFailureChecks:
    @pytest.mark.parametrize(
        ("module_name", "helper", "command"),
        (
            ("registry-utils.bat", "reg_set", "reg add"),
            ("telemetry-blocker.bat", "reg_add", "reg add"),
            ("debloater.bat", "reg_add", "reg add"),
            ("bcdedit-manager.bat", "bcd_set", "bcdedit /set"),
            ("bcdedit-manager.bat", "bcd_delete", "bcdedit /deletevalue"),
        ),
    )
    def test_mutating_command_is_followed_by_failure_branch(
        self, module_name, helper, command
    ):
        block = _label_block(_read(module_name), helper)
        command_position = block.lower().index(command)
        failure_position = block.lower().index("if errorlevel 1", command_position)
        counter_position = block.index("set /a MODULE_FAILURES+=1", failure_position)
        exit_position = block.lower().index("exit /b 1", counter_position)
        assert command_position < failure_position < counter_position < exit_position

    def test_bcdedit_export_failure_is_explicit(self):
        block = _label_block(_read("bcdedit-manager.bat"), "export_current")
        export_position = block.lower().index("bcdedit /export")
        failure_position = block.lower().index("if errorlevel 1", export_position)
        counter_position = block.index("set /a MODULE_FAILURES+=1", failure_position)
        exit_position = block.lower().index("exit /b 1", counter_position)
        assert export_position < failure_position < counter_position < exit_position

    @pytest.mark.skipif(os.name != "nt", reason="requires Windows CMD")
    @pytest.mark.parametrize("route", (":apply_safe_tweaks", ":apply_advanced_tweaks"))
    def test_bcdedit_route_returns_nonzero_with_failing_stub(self, tmp_path, route):
        stub = tmp_path / "failing-bcdedit.cmd"
        stub.write_text("@exit /b 17\n", encoding="utf-8")
        source = _read("bcdedit-manager.bat")
        sanitized = re.sub(
            r"(?im)^bcdedit\s+",
            lambda _: f'call "{stub}" ',
            source,
        )
        assert re.search(r"(?im)^bcdedit\s+", sanitized) is None
        module = tmp_path / "bcdedit-manager-sanitized.bat"
        module.write_text(sanitized, encoding="utf-8")
        runner = tmp_path / "run-route.cmd"
        runner.write_text(
            "@echo off\n"
            f'call "{module}" {route}\n'
            "set \"ROUTE_CODE=%ERRORLEVEL%\"\n"
            "exit /b %ROUTE_CODE%\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe"),
                "/d",
                "/c",
                str(runner),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode != 0
