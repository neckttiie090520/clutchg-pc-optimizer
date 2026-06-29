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

    def test_finds_exe_asset(self):
        assets = [
            {"name": "ClutchG-1.0.0.zip", "browser_download_url": "x"},
            {"name": "ClutchG-Setup-1.0.0.exe", "browser_download_url": "y"},
        ]
        checker = UpdateChecker("1.0.0")
        result = checker._find_installer_asset(assets)
        assert result is not None
        assert result["name"] == "ClutchG-Setup-1.0.0.exe"

    def test_returns_none_when_no_exe(self):
        assets = [
            {"name": "source.zip", "browser_download_url": "x"},
            {"name": "checksums.txt", "browser_download_url": "y"},
        ]
        checker = UpdateChecker("1.0.0")
        assert checker._find_installer_asset(assets) is None

    def test_empty_list_returns_none(self):
        assert UpdateChecker("1.0.0")._find_installer_asset([]) is None

    def test_case_insensitive_extension(self):
        assets = [{"name": "ClutchG.EXE", "browser_download_url": "x"}]
        checker = UpdateChecker("1.0.0")
        assert checker._find_installer_asset(assets) is not None

    def test_picks_first_exe_when_multiple(self):
        assets = [
            {"name": "a.exe", "browser_download_url": "x"},
            {"name": "b.exe", "browser_download_url": "y"},
        ]
        checker = UpdateChecker("1.0.0")
        result = checker._find_installer_asset(assets)
        assert result["name"] == "a.exe"

    def test_asset_missing_name_key_skipped(self):
        assets = [
            {"browser_download_url": "x"},  # no name
            {"name": "good.exe", "browser_download_url": "y"},
        ]
        checker = UpdateChecker("1.0.0")
        result = checker._find_installer_asset(assets)
        assert result["name"] == "good.exe"


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

    def test_returns_path_in_temp_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        path = UpdateChecker._create_relauncher_script("ClutchG-Setup-1.0.2.exe")
        assert path.parent == tmp_path / "clutchg_updates"
        assert path.exists()

    def test_filename_is_stable_relaunch_cmd(self, tmp_path, monkeypatch):
        # Stable filename means we don't accumulate copies across runs
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        path = UpdateChecker._create_relauncher_script("ClutchG-Setup-1.0.2.exe")
        assert path.name == "relaunch.cmd"

    def test_script_uses_name_based_polling_not_pid(self, tmp_path, monkeypatch):
        """Critical: must NOT poll by PID because UAC elevation respawns
        the installer with a different PID. Must poll by name instead."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        # Polling uses findstr on process name
        assert "findstr" in content
        assert "ClutchG-Setup" in content
        # Must NOT use PID-based polling
        assert "PID eq" not in content
        assert "INSTALLER_PID=" not in content

    def test_script_has_startup_window_for_uac(self, tmp_path, monkeypatch):
        """Must wait for installer to appear (handles slow UAC prompt)."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert ":startup_loop" in content
        assert "STARTUP_WAIT" in content

    def test_script_has_install_wait_loop(self, tmp_path, monkeypatch):
        """Must have a loop that waits for installer to finish."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert ":install_loop" in content
        assert "INSTALL_WAIT" in content

    def test_script_has_max_timeout(self, tmp_path, monkeypatch):
        """Must not wait forever — 600s (10 min) cap."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert "600" in content

    def test_script_queries_uninstall_registry(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert INNO_APP_ID in content
        assert "InstallLocation" in content

    def test_script_queries_both_hklm_and_hkcu(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert "HKLM" in content
        assert "HKCU" in content

    def test_script_launches_clutchg_exe(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert APP_EXE_NAME in content
        assert 'start ""' in content

    def test_script_self_deletes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert 'del "%~f0"' in content

    def test_script_uses_program_files_fallback(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert "ProgramFiles" in content
        assert APP_DIR_NAME in content

    def test_script_uses_localappdata_fallback(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert "LOCALAPPDATA" in content

    def test_script_is_ascii_only(self, tmp_path, monkeypatch):
        """Must be ASCII — em dashes or other Unicode crash cmd.exe on
        some locales and write_text(encoding='ascii')."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        # If this read succeeds, the file is ASCII-clean
        assert len(content) > 100

    def test_script_uses_delayed_expansion(self, tmp_path, monkeypatch):
        """Must use enabledelayedexpansion for the counter variables."""
        monkeypatch.setattr(
            "core.updater.tempfile.gettempdir", lambda: str(tmp_path)
        )
        content = UpdateChecker._create_relauncher_script(
            "ClutchG-Setup-1.0.2.exe"
        ).read_text("ascii")
        assert "enabledelayedexpansion" in content


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

    def test_returns_false_when_installer_missing(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        result = checker.install_update(tmp_path / "nonexistent.exe")
        assert result is False

    def test_returns_false_when_popen_raises(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        fake_exe = tmp_path / "fake.exe"
        fake_exe.write_text("dummy")

        with patch("core.updater.subprocess.Popen", side_effect=OSError("denied")):
            result = checker.install_update(fake_exe)

        assert result is False

    def test_does_not_spawn_relauncher_when_popen_fails(self, tmp_path):
        checker = UpdateChecker("1.0.0")
        fake_exe = tmp_path / "fake.exe"
        fake_exe.write_text("dummy")

        with patch("core.updater.subprocess.Popen", side_effect=OSError("denied")):
            with patch.object(checker, "_spawn_relauncher") as mock_spawn:
                checker.install_update(fake_exe)
                mock_spawn.assert_not_called()


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
