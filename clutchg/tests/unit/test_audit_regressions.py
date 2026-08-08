"""Regression tests for defects confirmed by the July 2026 audit."""

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from build import _clean_directory, __version__ as build_version
from core.action_catalog import TweakExecutionCatalog
from core.backup_manager import BackupInfo, BackupManager
from core.batch_executor import BatchExecutor, ExecutionResult
from core.profile_manager import ProfileManager
from utils.admin import AdminChecker


@pytest.mark.unit
class TestBackupSafetyRegressions:
    def test_index_path_escape_is_rejected_before_delete_or_restore(self, tmp_path):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        victim = tmp_path / "victim"
        registry_dir = victim / "registry"
        registry_dir.mkdir(parents=True)
        (registry_dir / "payload.reg").write_text("Windows Registry Editor", encoding="utf-8")

        malicious = {
            "id": "../victim",
            "name": "Escaped",
            "created_at": "2026-07-29T00:00:00",
            "profile": "TEST",
            "has_restore_point": False,
            "has_registry_backup": True,
            "description": "",
            "size_bytes": 0,
            "_success": True,
        }
        (backup_dir / "backup_index.json").write_text(
            json.dumps([malicious]), encoding="utf-8"
        )

        manager = BackupManager(backup_dir)
        assert manager.get_backup("../victim") is None

        manager.backups.append(BackupInfo(**malicious))
        with patch("subprocess.run") as mock_run:
            assert manager.restore_registry("../victim") is False
            assert manager.delete_backup("../victim") is False

        assert victim.exists()
        mock_run.assert_not_called()

    def test_backup_without_any_recovery_artifact_is_failed(self, tmp_path):
        manager = BackupManager(tmp_path / "backups")
        with patch.object(manager, "_create_restore_point", return_value=False), patch.object(
            manager, "_backup_registry", return_value=False
        ):
            backup = manager.create_backup("No recovery")

        assert backup is not None
        assert backup.success is False
        assert backup.has_restore_point is False
        assert backup.has_registry_backup is False

    def test_backup_views_require_successful_recovery_artifacts(self):
        repo_root = Path(__file__).parent.parent.parent.parent
        for relative_path in (
            "clutchg/src/gui/views/backup_minimal.py",
            "clutchg/src/gui/views/backup_restore_center.py",
        ):
            source = (repo_root / relative_path).read_text(encoding="utf-8")
            assert "if backup and backup.success:" in source

    def test_failed_tweak_snapshot_aborts_before_action(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)
        failed_snapshot = ExecutionResult(False, "", "snapshot failed", 1, 0.01)

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            executor_cls.return_value.execute.return_value = failed_snapshot
            result = manager.apply_tweaks(["tel_xbox_dvr"])

        assert result.success is False
        assert "snapshot failed" in result.errors.lower()
        executor_cls.return_value.execute.assert_called_once_with(
            scripts_dir / "safety" / "flight-recorder.bat",
            args=["create_snapshot"],
        )


@pytest.mark.unit
class TestExecutionSafetyRegressions:
    def test_selected_exact_scope_tweak_snapshots_before_dispatch(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)
        success = ExecutionResult(True, "", "", 0, 0.01)

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            executor_cls.return_value.execute.side_effect = [success, success]
            result = manager.apply_tweaks(["tel_xbox_dvr"])

        assert result.success is True
        assert executor_cls.return_value.execute.call_args_list == [
            call(
                scripts_dir / "safety" / "flight-recorder.bat",
                args=["create_snapshot"],
            ),
            call(
                scripts_dir / "core" / "telemetry-blocker.bat",
                args=[":apply_xbox_dvr"],
            ),
        ]

    def test_complete_overbroad_group_fails_before_backup_or_execution(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)

        with patch("core.backup_manager.BackupManager") as backup_cls, patch(
            "core.profile_manager.BatchExecutor"
        ) as executor_cls:
            result = manager.apply_tweaks(
                ["tel_advertising", "tel_cortana", "tel_activity", "tel_location"]
            )

        assert result.success is False
        assert "no audited execution contract" in result.errors.lower()
        backup_cls.assert_not_called()
        executor_cls.assert_not_called()

    def test_partial_shared_label_selection_fails_before_backup_or_execution(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)

        with patch("core.backup_manager.BackupManager") as backup_cls, patch(
            "core.profile_manager.BatchExecutor"
        ) as executor_cls:
            result = manager.apply_tweaks(["tel_advertising"])

        assert result.success is False
        assert "no audited execution contract" in result.errors.lower()
        backup_cls.assert_not_called()
        executor_cls.assert_not_called()

    def test_invalid_registry_route_fails_before_backup_or_execution(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)

        with patch("core.backup_manager.BackupManager") as backup_cls, patch(
            "core.profile_manager.BatchExecutor"
        ) as executor_cls:
            result = manager.apply_tweaks(["net_nagle", "net_window_size"])

        assert result.success is False
        assert "no audited execution contract" in result.errors.lower()
        backup_cls.assert_not_called()
        executor_cls.assert_not_called()

    def test_dispatch_parser_maps_argument_to_target_label(self, tmp_path):
        script = tmp_path / "routed.bat"
        script.write_text(
            '@echo off\nif "%~1"=="run_target" goto :target\ngoto :eof\n:target\n',
            encoding="utf-8",
        )

        routes = TweakExecutionCatalog.get_dispatch_routes(script)

        assert routes == {":target": frozenset({"run_target"})}

    def test_unknown_only_selection_fails_before_backup_or_execution(self):
        scripts_dir = Path(__file__).parent.parent.parent.parent / "src"
        manager = ProfileManager(scripts_dir)

        with patch("core.backup_manager.BackupManager") as backup_cls, patch(
            "core.profile_manager.BatchExecutor"
        ) as executor_cls:
            result = manager.apply_tweaks(["does_not_exist"])

        assert result.success is False
        assert "no audited execution contract" in result.errors.lower()
        backup_cls.assert_not_called()
        executor_cls.assert_not_called()

    def test_validation_exception_fails_closed_before_popen(self, tmp_path):
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n", encoding="utf-8")

        with patch("core.batch_parser.BatchParser", side_effect=RuntimeError("parser failed")), patch(
            "subprocess.Popen"
        ) as popen:
            result = BatchExecutor().execute(script)

        assert result.success is False
        assert result.return_code == -1
        assert "validation failed" in result.errors.lower()
        popen.assert_not_called()


@pytest.mark.unit
class TestElevationRegression:
    def test_frozen_relaunch_does_not_duplicate_executable_argument(self):
        checker = AdminChecker()
        shell32 = MagicMock()
        shell32.ShellExecuteW.return_value = 33

        with patch.object(checker, "is_admin", return_value=False), patch(
            "ctypes.windll"
        ) as windll, patch.object(sys, "frozen", True, create=True), patch.object(
            sys, "executable", r"C:\Program Files\ClutchG\ClutchG.exe"
        ), patch.object(
            sys, "argv", [r"C:\Program Files\ClutchG\ClutchG.exe", "--test-mode"]
        ), patch("sys.exit"):
            windll.shell32 = shell32
            checker.request_elevation()

        args = shell32.ShellExecuteW.call_args.args
        assert args[2] == r"C:\Program Files\ClutchG\ClutchG.exe"
        assert args[3] == "--test-mode"


@pytest.mark.unit
class TestBuildRegression:
    def test_clean_directory_removes_readonly_content(self, tmp_path):
        generated = tmp_path / "dist"
        readonly_dir = generated / "bundle" / "batch_scripts"
        readonly_dir.mkdir(parents=True)
        readonly_file = readonly_dir / "script.bat"
        readonly_file.write_text("@echo off\n", encoding="utf-8")
        os.chmod(readonly_file, stat.S_IREAD)
        os.chmod(readonly_dir, stat.S_IREAD)

        _clean_directory(generated)

        assert not generated.exists()

    def test_release_metadata_matches_canonical_version(self):
        """Every version surface must agree with ``src/version.py``.

        The version is read from the canonical source rather than hard-coded
        here. An earlier version of this test asserted the literal "1.0.3" in six
        places, so it failed on every release bump and taught the reader to edit
        the test instead of trusting it — the same drift this suite exists to
        catch. Comparing against ``__version__`` means the test keeps working
        across bumps while still catching a surface that was left behind.
        """
        project_dir = Path(__file__).parents[2]
        spec = (project_dir / "ClutchG.spec").read_text(encoding="utf-8")
        version_info = (project_dir / "version_info.txt").read_text(encoding="utf-8")
        settings = (project_dir / "src" / "gui" / "views" / "settings_minimal.py").read_text(
            encoding="utf-8"
        )
        package_init = (project_dir / "src" / "__init__.py").read_text(encoding="utf-8")
        build_script = (project_dir / "build.py").read_text(encoding="utf-8")

        canonical = re.search(
            r'__version__\s*=\s*"(\d+\.\d+\.\d+)"',
            (project_dir / "src" / "version.py").read_text(encoding="utf-8"),
        )
        assert canonical, "src/version.py does not declare __version__"
        version = canonical.group(1)
        major, minor, patch = version.split(".")

        assert build_version == version
        assert '"cpuinfo._cpuinfo"' not in spec
        assert f"filevers=({major}, {minor}, {patch}, 0)" in version_info
        assert f"prodvers=({major}, {minor}, {patch}, 0)" in version_info
        assert f"StringStruct(u'FileVersion',      u'{version}')" in version_info
        assert f"StringStruct(u'ProductVersion',   u'{version}')" in version_info
        assert '"about_version": "v{version} · Windows 10/11"' in settings
        assert "from version import __version__" in settings
        assert "from .version import __version__" in package_init
        assert "from src.version import __version__" in build_script
        assert "format(version=__version__)" in settings
        assert 'self.app.config.get("version"' not in settings

    def test_installer_and_default_config_agree_with_canonical_version(self):
        """The two surfaces the release CI also cross-checks."""
        project_dir = Path(__file__).parents[2]
        version = re.search(
            r'__version__\s*=\s*"(\d+\.\d+\.\d+)"',
            (project_dir / "src" / "version.py").read_text(encoding="utf-8"),
        ).group(1)

        installer = (project_dir / "installer" / "ClutchG.iss").read_text(encoding="utf-8")
        assert f'#define AppVersion   "{version}"' in installer

        config = (project_dir / "src" / "core" / "config.py").read_text(encoding="utf-8")
        assert f'"version": "{version}"' in config
