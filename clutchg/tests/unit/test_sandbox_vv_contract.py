"""Static contracts for the disposable Windows Sandbox V&V infrastructure.

These tests inspect configuration and harness source only. They do not launch
Windows Sandbox or execute privileged batch scripts.
"""

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SANDBOX_DIR = REPO_ROOT / "tests" / "sandbox"
CONFIGS = {
    "clutchg-test.wsb": "Enable",
    "clutchg-test-nogpu.wsb": "Enable",
    "clutchg-test-nonet.wsb": "Disable",
}
HOST_PATH_TOKENS = (
    "__CLUTCHG_SRC__",
    "__CLUTCHG_HARNESS__",
    "__CLUTCHG_RESULTS__",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.mark.unit
class TestSandboxConfigurationContract:
    @pytest.mark.parametrize(("name", "networking"), CONFIGS.items())
    def test_templates_are_portable_with_safe_permissions(self, name, networking):
        config = _read(SANDBOX_DIR / name)

        for token in HOST_PATH_TOKENS:
            assert config.count(f"<HostFolder>{token}</HostFolder>") == 1

        assert not re.search(r"<HostFolder>\s*[A-Za-z]:[\\/]", config)
        assert config.count("<ReadOnly>true</ReadOnly>") == 2
        assert config.count("<ReadOnly>false</ReadOnly>") == 1
        assert "C:\\ClutchG\\tests\\run-all-tests.bat" in config
        assert f"<Networking>{networking}</Networking>" in config
        assert "<vGPU>Disable</vGPU>" in config
        assert "thesis-doc\\project-code" not in config

    def test_host_launcher_materializes_xml_escaped_checkout_paths(self):
        launcher = _read(SANDBOX_DIR / "launch-tests.bat")

        assert 'for %%I in ("%SCRIPT_DIR%..\\..") do set "REPO_ROOT=%%~fI"' in launcher
        assert 'set "WSB_SRC=%REPO_ROOT%\\src"' in launcher
        assert 'set "WSB_HARNESS=%REPO_ROOT%\\tests\\sandbox"' in launcher
        assert 'set "WSB_RESULTS=%RESULTS_DIR%"' in launcher
        assert 'set "WSB_FILE=%TEMP%\\clutchg-sandbox-' in launcher
        assert launcher.count("[Security.SecurityElement]::Escape") == 3

        for token in HOST_PATH_TOKENS:
            assert f".Replace('{token}'," in launcher

        for name in CONFIGS:
            assert name in launcher

        assert 'start "" "%WSB_FILE%"' in launcher
        assert "where WindowsSandbox.exe" in launcher
        assert "vv-summary_*.txt" in launcher
        assert "Sandbox closed without producing results" in launcher

    def test_runner_writes_text_json_and_summary_evidence(self):
        runner = _read(SANDBOX_DIR / "run-all-tests.bat")

        assert "IMPORTANT: This runs with admin privileges inside the sandbox" in runner
        assert 'set "SRC=C:\\ClutchG\\src"' in runner
        assert "vv-results_%TIMESTAMP%.txt" in runner
        assert "vv-results_%TIMESTAMP%.json" in runner
        assert "vv-summary_%TIMESTAMP%.txt" in runner
        assert 'echo %TOTAL%,%PASSED%,%FAILED%,%SKIPPED%,%WARNED%' in runner
        assert 'call :group_header "SAFETY CONSTRAINT VERIFICATION"' in runner
        assert 'call :group_header "BACKUP-RESTORE CYCLE (Integration)"' in runner
