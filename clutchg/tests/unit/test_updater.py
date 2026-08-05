"""
Unit Tests for the Auto-Update system (core/updater.py).

Covers pure logic only:
  - Version parsing & comparison
  - Cooldown / opt-out gating
  - Asset selection from GitHub release JSON
  - DownloadProgress arithmetic & display
  - Relauncher script generation (content validation)
  - find_installed_clutchg_exe (filesystem fallback)

No network is touched. No subprocess is spawned.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.updater import (
    API_URL,
    APP_DIR_NAME,
    APP_EXE_NAME,
    ASSET_PATTERN,
    COOLDOWN_HOURS,
    INNO_APP_ID,
    UpdateChecker,
    DownloadProgress,
    UpdateInfo,
    is_newer_version,
    parse_version,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_info(**kwargs) -> UpdateInfo:
    defaults = dict(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="https://example.com/ClutchG-Setup-1.1.0.exe",
        asset_name="ClutchG-Setup-1.1.0.exe",
        asset_size=24_000_000,
        release_notes="Bug fixes",
        html_url="https://example.com/release/v1.1.0",
    )
    defaults.update(kwargs)
    return UpdateInfo(**defaults)


class _FakeConfigManager:
    """Minimal ConfigManager stand-in for should_check tests."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}

    def load_config(self) -> dict:
        return dict(self._config)

    def save_config(self, config: dict) -> None:
        self._config = dict(config)


# ---------------------------------------------------------------------------
# parse_version
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParseVersion:

    def test_plain_version(self):
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_v_prefix(self):
        assert parse_version("v1.2.3") == (1, 2, 3)

    def test_capital_v_prefix(self):
        assert parse_version("V1.2.3") == (1, 2, 3)

    def test_two_segments(self):
        assert parse_version("1.5") == (1, 5)

    def test_four_segments(self):
        assert parse_version("1.2.3.4") == (1, 2, 3, 4)

    def test_two_digit_segment(self):
        assert parse_version("1.10.0") == (1, 10, 0)

    def test_whitespace_stripped(self):
        assert parse_version("  1.0.0  ") == (1, 0, 0)

    def test_empty_returns_zero_tuple(self):
        assert parse_version("") == (0,)

    def test_invalid_returns_zero_tuple(self):
        assert parse_version("not-a-version") == (0,)

    def test_none_returns_zero_tuple(self):
        assert parse_version(None) == (0,)


# ---------------------------------------------------------------------------
# is_newer_version
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsNewerVersion:

    def test_newer_minor(self):
        assert is_newer_version("1.0.0", "1.1.0") is True

    def test_same_version_returns_false(self):
        assert is_newer_version("1.0.0", "1.0.0") is False

    def test_older_returns_false(self):
        assert is_newer_version("1.2.0", "1.1.0") is False

    def test_v_prefix_on_latest(self):
        assert is_newer_version("1.0.0", "v1.0.1") is True

    def test_v_prefix_on_both(self):
        assert is_newer_version("v1.0.0", "v2.0.0") is True

    def test_two_digit_segment_beats_single(self):
        # Critical edge case: 1.10 must be > 1.9 (lexicographic fails here)
        assert is_newer_version("1.9.0", "1.10.0") is True
        assert is_newer_version("1.10.0", "1.9.0") is False

    def test_different_segment_counts(self):
        assert is_newer_version("1.0", "1.0.1") is True
        assert is_newer_version("1.0.1", "1.0") is False


# ---------------------------------------------------------------------------
# UpdateChecker.should_check
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestShouldCheck:

    def test_no_config_manager_always_checks(self):
        checker = UpdateChecker("1.0.0", config_manager=None)
        assert checker.should_check() is True

    def test_opted_out_returns_false(self):
        cfg = _FakeConfigManager({"check_updates": False})
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        assert checker.should_check() is False

    def test_opted_in_default_true(self):
        cfg = _FakeConfigManager({})
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        assert checker.should_check() is True

    def test_within_cooldown_returns_false(self):
        cfg = _FakeConfigManager({
            "check_updates": True,
            "last_update_check": time.time(),  # just now
        })
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        assert checker.should_check() is False

    def test_past_cooldown_returns_true(self):
        # last check was COOLDOWN_HOURS + 1 ago
        cfg = _FakeConfigManager({
            "check_updates": True,
            "last_update_check": time.time() - (COOLDOWN_HOURS + 1) * 3600,
        })
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        assert checker.should_check() is True

    def test_cooldown_boundary_exactly_at_limit(self):
        # Exactly COOLDOWN_HOURS ago — should check (>= comparison)
        cfg = _FakeConfigManager({
            "check_updates": True,
            "last_update_check": time.time() - COOLDOWN_HOURS * 3600,
        })
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        # Allow small float slack: boundary itself should be True (>=)
        assert checker.should_check() is True


# ---------------------------------------------------------------------------
# UpdateChecker._find_installer_asset
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFindInstallerAsset:

    @staticmethod
    def _asset(version="1.0.0", **overrides):
        name = f"ClutchG-Setup-{version}.exe"
        asset = {
            "name": name,
            "browser_download_url": (
                "https://github.com/neckttiie090520/clutchg-pc-optimizer/"
                f"releases/download/v{version}/{name}"
            ),
            "state": "uploaded",
        }
        asset.update(overrides)
        return asset

    def test_finds_exact_versioned_release_asset(self):
        assets = [
            {"name": "ClutchG-1.0.0.zip", "browser_download_url": "x"},
            self._asset(),
        ]
        result = UpdateChecker("1.0.0")._find_installer_asset(assets)
        assert result == assets[1]

    def test_returns_none_when_no_exact_installer(self):
        assets = [
            {"name": "source.zip", "browser_download_url": "x"},
            {"name": "checksums.txt", "browser_download_url": "y"},
        ]
        assert UpdateChecker("1.0.0")._find_installer_asset(assets) is None

    def test_empty_list_returns_none(self):
        assert UpdateChecker("1.0.0")._find_installer_asset([]) is None

    def test_rejects_case_or_filename_variants(self):
        asset = self._asset(name="CLUTCHG-SETUP-1.0.0.EXE")
        assert UpdateChecker("1.0.0")._find_installer_asset([asset]) is None

    def test_rejects_duplicate_exact_assets(self):
        asset = self._asset()
        assert UpdateChecker("1.0.0")._find_installer_asset([asset, dict(asset)]) is None

    def test_rejects_wrong_version_or_host(self):
        checker = UpdateChecker("1.0.0")
        assert checker._find_installer_asset([self._asset("1.1.0")]) is None
        wrong_host = self._asset(
            browser_download_url=(
                "https://example.com/neckttiie090520/clutchg-pc-optimizer/"
                "releases/download/v1.0.0/ClutchG-Setup-1.0.0.exe"
            )
        )
        assert checker._find_installer_asset([wrong_host]) is None

    def test_asset_missing_name_key_is_rejected(self):
        assert UpdateChecker("1.0.0")._find_installer_asset(
            [{"browser_download_url": "x"}]
        ) is None


@pytest.mark.unit
class TestUniqueDownloadDirectory:

    def test_each_download_uses_a_unique_attempt_directory(self, tmp_path):
        payload = b"signed-installer-placeholder"
        info = _make_info(
            download_url=(
                "https://github.com/neckttiie090520/clutchg-pc-optimizer/"
                "releases/download/v1.1.0/ClutchG-Setup-1.1.0.exe"
            ),
            asset_size=len(payload),
        )
        attempt = 0

        def _mkdtemp(prefix):
            nonlocal attempt
            attempt += 1
            path = tmp_path / f"{prefix}{attempt}"
            path.mkdir()
            return str(path)

        def _response():
            response = MagicMock()
            response.headers = {"Content-Length": str(len(payload))}
            response.read.side_effect = [payload, b""]
            response.__enter__.return_value = response
            return response

        checker = UpdateChecker("1.0.0")
        with patch("core.updater.tempfile.mkdtemp", side_effect=_mkdtemp), patch(
            "core.updater.urlopen", side_effect=[_response(), _response()]
        ):
            first = checker.download_update(info)
            second = checker.download_update(info)

        assert first is not None
        assert second is not None
        assert first.parent != second.parent
        assert first.parent.name.startswith("clutchg-update-")
        assert second.parent.name.startswith("clutchg-update-")


# ---------------------------------------------------------------------------
# DownloadProgress
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDownloadProgress:

    def test_percent_zero_when_total_unknown(self):
        p = DownloadProgress(downloaded=100, total=0)
        assert p.percent == 0.0

    def test_percent_zero_when_total_negative(self):
        p = DownloadProgress(downloaded=100, total=-5)
        assert p.percent == 0.0

    def test_percent_halfway(self):
        p = DownloadProgress(downloaded=50, total=100)
        assert p.percent == 50.0

    def test_percent_capped_at_100(self):
        p = DownloadProgress(downloaded=150, total=100)
        assert p.percent == 100.0

    def test_speed_display_bytes(self):
        p = DownloadProgress(speed_bps=500)
        assert p.speed_display == "500 B/s"

    def test_speed_display_kilobytes(self):
        p = DownloadProgress(speed_bps=2048)
        assert p.speed_display == "2.0 KB/s"

    def test_speed_display_megabytes(self):
        p = DownloadProgress(speed_bps=2 * 1024 * 1024)
        assert p.speed_display == "2.0 MB/s"

    def test_size_display_kilobytes(self):
        p = DownloadProgress(total=500 * 1024)
        assert p.size_display == "500 KB"

    def test_size_display_megabytes(self):
        p = DownloadProgress(total=24 * 1024 * 1024)
        assert p.size_display == "24.0 MB"

    def test_default_values(self):
        p = DownloadProgress()
        assert p.downloaded == 0
        assert p.total == 0
        assert p.speed_bps == 0.0
        assert p.percent == 0.0


# ---------------------------------------------------------------------------
# _record_check_time
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRecordCheckTime:

    def test_writes_timestamp_to_config(self):
        cfg = _FakeConfigManager({"check_updates": True})
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        before = time.time()
        checker._record_check_time()
        after = time.time()
        saved = cfg.load_config()["last_update_check"]
        assert before <= saved <= after

    def test_no_config_manager_does_nothing(self):
        checker = UpdateChecker("1.0.0", config_manager=None)
        # Should not raise
        checker._record_check_time()

    def test_save_failure_does_not_raise(self):
        cfg = MagicMock()
        cfg.load_config.side_effect = Exception("disk full")
        checker = UpdateChecker("1.0.0", config_manager=cfg)
        checker._record_check_time()  # must not raise


# ---------------------------------------------------------------------------
# _cleanup_file
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCleanupFile:

    def test_removes_existing_file(self, tmp_path):
        f = tmp_path / "stale.exe"
        f.write_text("dummy")
        UpdateChecker._cleanup_file(f)
        assert not f.exists()

    def test_missing_file_does_not_raise(self, tmp_path):
        f = tmp_path / "nonexistent.exe"
        UpdateChecker._cleanup_file(f)  # must not raise


# ---------------------------------------------------------------------------
# _create_relauncher_script (content validation — no subprocess)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateRelauncherScript:

    @staticmethod
    def _create(tmp_path):
        staging_dir = tmp_path / "update-test"
        staging_dir.mkdir()
        path = UpdateChecker._create_relauncher_script(
            staging_dir, "ClutchG-Setup-1.0.2.exe"
        )
        return staging_dir, path, path.read_text("ascii")

    def test_returns_relauncher_inside_staging(self, tmp_path):
        staging_dir, path, _ = self._create(tmp_path)
        assert path == staging_dir / "relaunch.cmd"
        assert path.exists()

    def test_script_uses_name_based_polling_not_pid(self, tmp_path):
        _, _, content = self._create(tmp_path)
        assert "findstr" in content
        assert "ClutchG-Setup-1.0.2.exe" in content
        assert "PID eq" not in content
        assert "INSTALLER_PID=" not in content

    def test_script_waits_with_bounded_timeouts(self, tmp_path):
        _, _, content = self._create(tmp_path)
        assert ":startup_loop" in content
        assert "STARTUP_WAIT" in content
        assert ":install_loop" in content
        assert "INSTALL_WAIT" in content
        assert "600" in content

    def test_script_locates_and_launches_installed_app(self, tmp_path):
        _, _, content = self._create(tmp_path)
        assert INNO_APP_ID in content
        assert "HKLM" in content
        assert "HKCU" in content
        assert "InstallLocation" in content
        assert "ProgramFiles" in content
        assert "LOCALAPPDATA" in content
        assert APP_DIR_NAME in content
        assert APP_EXE_NAME in content
        assert 'start ""' in content

    def test_script_cleans_installer_script_and_staging_dir(self, tmp_path):
        _, _, content = self._create(tmp_path)
        assert 'del /f /q "%~dp0ClutchG-Setup-1.0.2.exe"' in content
        assert 'del /f /q "%~f0"' in content
        assert 'rd "%%~fD"' in content

    def test_script_is_ascii_and_uses_delayed_expansion(self, tmp_path):
        _, path, content = self._create(tmp_path)
        assert path.read_bytes().decode("ascii").replace("\r\n", "\n") == content
        assert "enabledelayedexpansion" in content

    def test_rejects_missing_staging_directory(self, tmp_path):
        with pytest.raises(ValueError):
            UpdateChecker._create_relauncher_script(
                tmp_path / "missing", "ClutchG-Setup-1.0.2.exe"
            )


# ---------------------------------------------------------------------------
# find_installed_clutchg_exe (filesystem fallback path only)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFindInstalledClutchgExe:

    def test_returns_none_when_nothing_exists(self, monkeypatch):
        # Registry lookup should raise OSError (no key), forcing fallback.
        # Filesystem fallback also returns nothing.
        import winreg

        def _open_key_raises(*args, **kwargs):
            raise OSError("not found")

        monkeypatch.setattr(winreg, "OpenKey", _open_key_raises)
        monkeypatch.setenv("ProgramFiles", r"C:\fake_pf")
        monkeypatch.setenv("ProgramFiles(x86)", r"C:\fake_pf_x86")
        monkeypatch.setenv("LOCALAPPDATA", r"C:\fake_la")
        assert UpdateChecker.find_installed_clutchg_exe() is None

    def test_finds_program_files_install(self, monkeypatch, tmp_path):
        import winreg

        install_dir = tmp_path / "ClutchG"
        install_dir.mkdir()
        exe = install_dir / "ClutchG.exe"
        exe.write_text("dummy")

        def _open_key_raises(*args, **kwargs):
            raise OSError("not found")

        monkeypatch.setattr(winreg, "OpenKey", _open_key_raises)
        monkeypatch.setenv("ProgramFiles", str(install_dir.parent))
        monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "x86missing"))
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "lamissing"))

        result = UpdateChecker.find_installed_clutchg_exe()
        assert result == exe

    def test_finds_per_user_install(self, monkeypatch, tmp_path):
        import winreg

        programs_dir = tmp_path / "Programs" / "ClutchG"
        programs_dir.mkdir(parents=True)
        exe = programs_dir / "ClutchG.exe"
        exe.write_text("dummy")

        def _open_key_raises(*args, **kwargs):
            raise OSError("not found")

        monkeypatch.setattr(winreg, "OpenKey", _open_key_raises)
        # Program Files fallback: empty dir
        monkeypatch.setenv("ProgramFiles", str(tmp_path / "no_pf"))
        monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "no_pf_x86"))
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

        result = UpdateChecker.find_installed_clutchg_exe()
        assert result == exe

    def test_finds_via_registry_install_location(self, monkeypatch, tmp_path):
        import winreg

        install_dir = tmp_path / "ClutchG"
        install_dir.mkdir()
        exe = install_dir / "ClutchG.exe"
        exe.write_text("dummy")

        # Fake registry context manager
        class _FakeKey:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def _open_key(hive, key_path):
            assert INNO_APP_ID in key_path
            return _FakeKey()

        def _query_value(key, name):
            assert name == "InstallLocation"
            return (str(install_dir), winreg.REG_SZ)

        monkeypatch.setattr(winreg, "OpenKey", _open_key)
        monkeypatch.setattr(winreg, "QueryValueEx", _query_value)

        result = UpdateChecker.find_installed_clutchg_exe()
        assert result == exe


# ---------------------------------------------------------------------------
# UpdateInfo dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestUpdateInfo:

    def test_defaults_release_notes_empty(self):
        info = _make_info(release_notes=None)
        # The dataclass allows empty string default; with None passed
        # explicitly we expect None to persist
        assert info.release_notes is None

    def test_html_url_default_empty(self):
        info = _make_info(html_url=None)
        assert info.html_url is None


# ---------------------------------------------------------------------------
# install_update / AsyncUpdateChecker.install (return value contract)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestInstallUpdateReturnContract:

    @staticmethod
    def _installer(tmp_path, version="1.1.0"):
        download_dir = tmp_path / "clutchg-update-download"
        download_dir.mkdir()
        path = download_dir / f"ClutchG-Setup-{version}.exe"
        path.write_bytes(b"signed installer bytes")
        return path

    def test_returns_false_when_installer_missing(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        result = checker.install_update(tmp_path / "nonexistent.exe")
        assert result is False

    def test_staging_failure_aborts_before_copy_or_launch(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = self._installer(tmp_path)
        with patch.object(
            checker, "_create_secure_staging_dir", return_value=None
        ), patch("core.updater.shutil.copyfile") as copyfile, patch(
            "core.updater.subprocess.Popen"
        ) as popen:
            assert checker.install_update(installer) is False
        copyfile.assert_not_called()
        popen.assert_not_called()
        assert not installer.exists()

    def test_verifies_staged_copy_and_cleans_on_rejection(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = self._installer(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        staged_installer = staging_dir / installer.name
        with patch.object(
            checker, "_create_secure_staging_dir", return_value=staging_dir
        ), patch.object(
            checker, "verify_installer", return_value=False
        ) as verify, patch("core.updater.subprocess.Popen") as popen:
            assert checker.install_update(installer) is False
        verify.assert_called_once_with(staged_installer)
        popen.assert_not_called()
        assert not staging_dir.exists()
        assert not installer.exists()

    def test_final_fingerprint_mismatch_prevents_launch(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = self._installer(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        relauncher = staging_dir / "relaunch.cmd"
        with patch.object(
            checker, "_create_secure_staging_dir", return_value=staging_dir
        ), patch.object(
            checker, "verify_installer", return_value=True
        ), patch.object(
            checker, "_sha256_file", side_effect=["same", "same", "changed"]
        ), patch.object(
            checker, "_create_relauncher_script", return_value=relauncher
        ), patch("core.updater.subprocess.Popen") as popen:
            assert checker.install_update(installer) is False
        popen.assert_not_called()
        assert not staging_dir.exists()
        assert not installer.exists()

    def test_handoff_failure_stops_started_staged_installer(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = self._installer(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        relauncher = staging_dir / "relaunch.cmd"
        process = MagicMock(pid=123)
        with patch.object(
            checker, "_create_secure_staging_dir", return_value=staging_dir
        ), patch.object(checker, "verify_installer", return_value=True), patch.object(
            checker, "_create_relauncher_script", return_value=relauncher
        ), patch("core.updater.subprocess.Popen", return_value=process), patch.object(
            checker, "_spawn_relauncher_script", return_value=False
        ):
            assert checker.install_update(installer) is False
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=5)
        assert not staging_dir.exists()
        assert not installer.exists()

    def test_success_launches_staged_path_and_hands_off_cleanup(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = self._installer(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        staged_installer = staging_dir / installer.name
        relauncher = staging_dir / "relaunch.cmd"
        process = MagicMock(pid=123)
        with patch.object(
            checker, "_create_secure_staging_dir", return_value=staging_dir
        ), patch.object(
            checker, "verify_installer", return_value=True
        ) as verify, patch.object(
            checker, "_create_relauncher_script", return_value=relauncher
        ), patch("core.updater.subprocess.Popen", return_value=process) as popen, patch.object(
            checker, "_spawn_relauncher_script", return_value=True
        ) as spawn:
            assert checker.install_update(installer, silent=True) is True
        verify.assert_called_once_with(staged_installer)
        command = popen.call_args.args[0]
        assert command == [
            str(staged_installer),
            "/SILENT",
            "/CLOSEAPPLICATIONS",
            "/CLUTCHGUPDATE",
        ]
        spawn.assert_called_once_with(relauncher)
        assert staged_installer.exists()
        assert not installer.exists()


@pytest.mark.unit
class TestSecureStaging:

    def test_root_acl_failure_aborts_before_child_creation(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("ProgramData", str(tmp_path))
        staging_root = tmp_path / "ClutchG" / "Updates"
        with patch("core.updater.sys.platform", "win32"), patch.object(
            UpdateChecker, "_is_reparse_point", return_value=False
        ), patch.object(
            UpdateChecker, "_secure_staging_dir", return_value=False
        ) as secure:
            assert UpdateChecker._create_secure_staging_dir() is None
        secure.assert_called_once_with(staging_root)
        assert not list(staging_root.glob("update-*"))

    def test_child_acl_failure_removes_unique_staging(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("ProgramData", str(tmp_path))
        staging_root = tmp_path / "ClutchG" / "Updates"
        staging_dir = staging_root / f"update-{'a' * 32}"
        with patch("core.updater.sys.platform", "win32"), patch(
            "core.updater.secrets.token_hex", return_value="a" * 32
        ), patch.object(
            UpdateChecker, "_is_reparse_point", return_value=False
        ), patch.object(
            UpdateChecker, "_secure_staging_dir", side_effect=[True, False]
        ) as secure:
            assert UpdateChecker._create_secure_staging_dir() is None
        assert secure.call_args_list == [
            ((staging_root,),),
            ((staging_dir,),),
        ]
        assert not staging_dir.exists()

    def test_create_secure_staging_hardens_root_and_unique_child(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("ProgramData", str(tmp_path))
        staging_root = tmp_path / "ClutchG" / "Updates"
        staging_dir = staging_root / f"update-{'b' * 32}"
        with patch("core.updater.sys.platform", "win32"), patch(
            "core.updater.secrets.token_hex", return_value="b" * 32
        ), patch.object(
            UpdateChecker, "_is_reparse_point", return_value=False
        ), patch.object(
            UpdateChecker, "_secure_staging_dir", return_value=True
        ) as secure:
            assert UpdateChecker._create_secure_staging_dir() == staging_dir
        assert secure.call_args_list == [
            ((staging_root,),),
            ((staging_dir,),),
        ]
        assert staging_dir.is_dir()

    def test_secure_staging_applies_acl_integrity_and_verifies(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        success = MagicMock(returncode=0, stdout="", stderr="")
        with patch("core.updater.subprocess.run", return_value=success) as run:
            assert UpdateChecker._secure_staging_dir(staging_dir) is True
        assert run.call_count == 3
        commands = [call.args[0] for call in run.call_args_list]
        assert commands[0][0] == "icacls.exe"
        assert "/inheritance:r" in commands[0]
        assert "*S-1-5-18:(OI)(CI)F" in commands[0]
        assert "*S-1-5-32-544:(OI)(CI)F" in commands[0]
        assert "/setintegritylevel" in commands[1]
        assert commands[2][0] == "powershell.exe"

    def test_secure_staging_fails_closed_on_acl_command_error(self, tmp_path):
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()
        failure = MagicMock(returncode=5, stdout="", stderr="denied")
        with patch("core.updater.subprocess.run", return_value=failure):
            assert UpdateChecker._secure_staging_dir(staging_dir) is False


@pytest.mark.unit
class TestInstallerAuthenticodeVerification:

    def test_accepts_trusted_expected_publisher_and_matching_version(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = TestInstallUpdateReturnContract._installer(tmp_path)
        with patch("core.updater.sys.platform", "win32"), patch(
            "core.updater._win_verify_trust", return_value=True
        ), patch.object(
            checker,
            "_get_installer_metadata",
            return_value=("CN=ClutchG Project", "1.1.0"),
        ):
            assert checker.verify_installer(installer) is True

    def test_rejects_untrusted_signature_before_metadata_read(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        installer = TestInstallUpdateReturnContract._installer(tmp_path)
        with patch("core.updater.sys.platform", "win32"), patch(
            "core.updater._win_verify_trust", return_value=False
        ), patch.object(checker, "_get_installer_metadata") as metadata:
            assert checker.verify_installer(installer) is False
        metadata.assert_not_called()

    @pytest.mark.parametrize(
        "metadata",
        [
            ("CN=Unexpected Publisher", "1.1.0"),
            ("CN=ClutchG Project", "9.9.9"),
            None,
        ],
    )
    def test_rejects_publisher_version_or_metadata_mismatch(self, tmp_path, metadata):
        checker = UpdateChecker("1.0.0")
        installer = TestInstallUpdateReturnContract._installer(tmp_path)
        with patch("core.updater.sys.platform", "win32"), patch(
            "core.updater._win_verify_trust", return_value=True
        ), patch.object(checker, "_get_installer_metadata", return_value=metadata):
            assert checker.verify_installer(installer) is False


# ---------------------------------------------------------------------------
# AsyncUpdateChecker.install passthrough
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAsyncInstallPassthrough:

    def test_install_returns_bool_from_underlying_checker(self, tmp_path):
        from core.updater import AsyncUpdateChecker

        fake_exe = tmp_path / "fake.exe"
        fake_exe.write_text("dummy")

        window = MagicMock()
        async_checker = AsyncUpdateChecker(window, "1.0.0")

        with patch.object(async_checker.checker, "install_update", return_value=True) as m:
            result = async_checker.install(fake_exe)
            assert result is True
            m.assert_called_once_with(fake_exe, silent=False)

    def test_install_passes_silent_flag(self, tmp_path):
        from core.updater import AsyncUpdateChecker

        fake_exe = tmp_path / "fake.exe"
        fake_exe.write_text("dummy")

        window = MagicMock()
        async_checker = AsyncUpdateChecker(window, "1.0.0")

        with patch.object(async_checker.checker, "install_update", return_value=False) as m:
            result = async_checker.install(fake_exe, silent=True)
            assert result is False
            m.assert_called_once_with(fake_exe, silent=True)
