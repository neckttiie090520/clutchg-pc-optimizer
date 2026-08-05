"""Static fail-closed contracts for the Windows release pipeline.

These tests inspect workflow and installer source only. They never build, sign,
publish, or execute an installer.
"""

from pathlib import Path
import re

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release.yml"
INSTALLER = REPO_ROOT / "clutchg" / "installer" / "ClutchG.iss"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _step_block(workflow: str, name: str, next_name: str | None = None) -> str:
    start = workflow.index(f"      - name: {name}\n")
    if next_name is None:
        return workflow[start:]
    end = workflow.index(f"      - name: {next_name}\n", start)
    return workflow[start:end]


@pytest.mark.unit
class TestReleaseIdentityContract:
    def test_tag_and_all_version_sources_must_match(self):
        workflow = _read(WORKFLOW)

        assert "Release tag must be exactly vMAJOR.MINOR.PATCH" in workflow
        assert "clutchg/src/version.py" in workflow
        assert "clutchg/installer/ClutchG.iss" in workflow
        assert "clutchg/version_info.txt" in workflow
        assert "$pythonVersion, $installerVersion, $fileVersion, $productVersion" in workflow
        assert "Where-Object { $_ -ne $version }" in workflow

    def test_release_uses_one_exact_versioned_asset(self):
        workflow = _read(WORKFLOW)

        assert 'ClutchG-Setup-$version.exe' in workflow
        assert "$assets.Count -ne 1" in workflow
        assert "Unexpected installer asset" in workflow
        assert "files: ${{ steps.identity.outputs.installer }}" in workflow
        assert "files: clutchg/installer/output/ClutchG-Setup-*.exe" not in workflow
        assert 'ClutchG-Setup-*.exe" | Select-Object -First 1' not in workflow

    def test_every_external_action_is_pinned_to_full_commit_sha(self):
        workflow = _read(WORKFLOW)
        uses_refs = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, re.MULTILINE)

        assert uses_refs
        assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", ref) for ref in uses_refs)
        assert "actions/checkout@v" not in workflow
        assert "actions/setup-python@v" not in workflow
        assert "softprops/action-gh-release@v" not in workflow


@pytest.mark.unit
class TestReleaseSigningContract:
    def test_certificate_secrets_and_exact_publisher_are_required(self):
        workflow = _read(WORKFLOW)

        assert "WINDOWS_SIGNING_CERTIFICATE_BASE64 is not provisioned" in workflow
        assert "WINDOWS_SIGNING_CERTIFICATE_PASSWORD is not provisioned" in workflow
        assert "EXPECTED_PUBLISHER: CN=ClutchG Project" in workflow
        assert "$certificate.Subject -ne $env:EXPECTED_PUBLISHER" in workflow
        assert "$certificate.HasPrivateKey" in workflow

    def test_signing_secrets_are_step_scoped_only(self):
        workflow = _read(WORKFLOW)
        job_prefix = workflow[: workflow.index("    steps:\n")]

        assert "secrets.WINDOWS_SIGNING_CERTIFICATE" not in job_prefix
        assert workflow.count("secrets.WINDOWS_SIGNING_CERTIFICATE_BASE64") == 2
        assert workflow.count("secrets.WINDOWS_SIGNING_CERTIFICATE_PASSWORD") == 4

        release = _step_block(workflow, "Create GitHub Release")
        assert "secrets." not in release
        for step_name in (
            "Install runtime dependencies",
            "Install test dependencies",
            "Run tests",
            "Build ClutchG.exe",
            "Build Inno Setup installer",
        ):
            block = _step_block(
                workflow,
                step_name,
                {
                    "Install runtime dependencies": "Install test dependencies",
                    "Install test dependencies": "Run tests",
                    "Run tests": "Build ClutchG.exe",
                    "Build ClutchG.exe": "Prepare signing certificate",
                    "Build Inno Setup installer": "Prepare installer signing certificate",
                }[step_name],
            )
            assert "secrets." not in block

    def test_app_and_installer_are_signed_and_verified(self):
        workflow = _read(WORKFLOW)

        assert "Sign and verify ClutchG.exe" in workflow
        assert "Sign and verify exact installer" in workflow
        assert workflow.count("& $env:SIGNTOOL_PATH sign") == 2
        assert workflow.count("Get-AuthenticodeSignature -LiteralPath") == 2
        assert workflow.count("$signature.Status -ne 'Valid'") == 2
        assert workflow.count("$signature.SignerCertificate.Subject -ne $env:EXPECTED_PUBLISHER") == 2
        assert workflow.count("ProductVersion mismatch") == 2

    def test_pfx_has_two_narrow_signing_windows_and_fixed_cleanup_path(self):
        workflow = _read(WORKFLOW)

        assert "SIGNING_CERTIFICATE_PATH: ${{ runner.temp }}\\clutchg-signing.pfx" in workflow
        assert workflow.count("[IO.File]::WriteAllBytes(") == 2
        assert workflow.count("if: always()") >= 2
        assert workflow.count(
            "Remove-Item -LiteralPath $env:SIGNING_CERTIFICATE_PATH -Force"
        ) >= 2

        build_app = workflow.index("      - name: Build ClutchG.exe\n")
        prepare_app = workflow.index("      - name: Prepare signing certificate\n")
        sign_app = workflow.index("      - name: Sign and verify ClutchG.exe\n")
        cleanup_app = workflow.index("      - name: Remove app signing material\n")
        build_installer = workflow.index("      - name: Build Inno Setup installer\n")
        prepare_installer = workflow.index(
            "      - name: Prepare installer signing certificate\n"
        )
        sign_installer = workflow.index("      - name: Sign and verify exact installer\n")
        cleanup_installer = workflow.index("      - name: Remove signing material\n")
        release = workflow.index("      - name: Create GitHub Release\n")

        assert (
            build_app
            < prepare_app
            < sign_app
            < cleanup_app
            < build_installer
            < prepare_installer
            < sign_installer
            < cleanup_installer
            < release
        )


@pytest.mark.unit
class TestInstallerRestartOwnership:
    def test_updater_is_the_only_post_install_restart_owner(self):
        installer = _read(INSTALLER)

        assert "RestartApplications=no" in installer
        assert "RestartApplications=yes" not in installer
