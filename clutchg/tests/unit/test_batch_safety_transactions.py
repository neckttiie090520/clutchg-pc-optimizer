"""Static contract tests for journaled batch backup and rollback.

These tests read batch files as text. They never execute CMD, registry, PowerShell,
PowerCfg, BCDEdit, service, restore-point, or installer commands.
"""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKUP = REPO_ROOT / "src" / "backup" / "backup-registry.bat"
RESTORE_POINT = REPO_ROOT / "src" / "backup" / "restore-point.bat"
ROLLBACK = REPO_ROOT / "src" / "safety" / "rollback.bat"
FLIGHT_RECORDER = REPO_ROOT / "src" / "safety" / "flight-recorder.bat"
EXTREME_ROLLBACK = REPO_ROOT / "src" / "safety" / "extreme-rollback.bat"

VALUE_COMPONENTS = (
    "value_gameconfig_dvr",
    "value_policy_gamedvr",
    "value_policy_allowgamedvr",
    "value_machine_gamedvr",
    "value_user_gamedvr",
    "value_gamebar_nexus",
    "value_gamebar_startup",
    "value_presencewriter_activation",
    "value_gamebar_allowgamemode",
    "value_gamebar_automode",
    "value_copilot_hkcu",
    "value_copilot_hklm",
    "value_windowsai_hkcu",
    "value_windowsai_hklm",
    "value_copilot_button",
)
VALUE_TARGETS = {
    "value_gameconfig_dvr": (r"HKCU\System\GameConfigStore", "GameDVR_Enabled"),
    "value_policy_gamedvr": (
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR",
        "AllowGameDVR",
    ),
    "value_policy_allowgamedvr": (
        r"HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR",
        "value",
    ),
    "value_machine_gamedvr": (
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
        "AppCaptureEnabled",
    ),
    "value_user_gamedvr": (
        r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
        "AppCaptureEnabled",
    ),
    "value_gamebar_nexus": (
        r"HKCU\Software\Microsoft\GameBar",
        "UseNexusForGameBarEnabled",
    ),
    "value_gamebar_startup": (
        r"HKCU\Software\Microsoft\GameBar",
        "ShowStartupPanel",
    ),
    "value_presencewriter_activation": (
        r"HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter",
        "ActivationType",
    ),
    "value_gamebar_allowgamemode": (
        r"HKCU\Software\Microsoft\GameBar",
        "AllowAutoGameMode",
    ),
    "value_gamebar_automode": (
        r"HKCU\Software\Microsoft\GameBar",
        "AutoGameModeEnabled",
    ),
    "value_copilot_hkcu": (
        r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot",
        "TurnOffWindowsCopilot",
    ),
    "value_copilot_hklm": (
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot",
        "TurnOffWindowsCopilot",
    ),
    "value_windowsai_hkcu": (
        r"HKCU\Software\Policies\Microsoft\Windows\WindowsAI",
        "DisableAIDataAnalysis",
    ),
    "value_windowsai_hklm": (
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
        "DisableAIDataAnalysis",
    ),
    "value_copilot_button": (
        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "ShowCopilotButton",
    ),
}
COMPONENTS = VALUE_COMPONENTS + (
    "services",
    "bcd",
    "power_scheme",
    "system_info",
)
SERVICE_NAMES = (
    "DiagTrack",
    "dmwappushservice",
    "diagnosticshub.standardcollector.service",
    "SysMain",
    "WSearch",
    "XblAuthManager",
    "XblGameSave",
    "XboxNetApiSvc",
    "XboxGipSvc",
    "RetailDemo",
    "MapsBroker",
    "lfsvc",
    "SharedAccess",
    "Fax",
    "WFDSConMgrSvc",
    "TabletInputService",
    "Spooler",
    "SEMgrSvc",
    "RmSvc",
    "WalletService",
    "UsoSvc",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _section(content: str, label: str, next_label: str) -> str:
    """Return text between two exact batch label definition lines."""
    start_marker = f"\n:{label}\n"
    end_marker = f"\n:{next_label}\n"
    start = content.index(start_marker) + 1
    end = content.index(end_marker, start)
    return content[start:end]


@pytest.mark.unit
class TestBackupTransactionContract:
    def test_manifest_and_journal_commit_only_after_all_capture_steps(self):
        content = _read(BACKUP)

        assert "format=clutchg-backup-v1" in content
        assert "state=PREPARING" in content
        assert "BEGIN^|!BACKUP_ID!" in content
        assert "if !BACKUP_FAILED! EQU 0" in content
        assert 'set "FINAL_STATE=COMMITTED"' in content
        assert 'set "RETURN_CODE=1"' in content
        assert "END^|!FINAL_STATE!^|success=!BACKUP_SUCCESS!^|failed=!BACKUP_FAILED!" in content

        capture_block = _section(content, "create_backup", "write_manifest_header")
        capture_positions = [
            capture_block.index(f"call :{label}")
            for label in (
                "backup_registry",
                "backup_services",
                "backup_bcd",
                "backup_power_scheme",
                "backup_system_info",
            )
        ]
        assert capture_positions == sorted(capture_positions)
        assert max(capture_positions) < capture_block.index('set "FINAL_STATE=COMMITTED"')

    def test_manifest_enumerates_every_restorable_component(self):
        content = _read(BACKUP)
        registry_block = _section(content, "backup_registry", "backup_registry_value")

        assert "components=" + ",".join(COMPONENTS) in content
        for component in VALUE_COMPONENTS:
            assert f'call :backup_registry_value "{component}"' in registry_block
        for component in COMPONENTS[len(VALUE_COMPONENTS) :]:
            assert f'call :record_result "{component}"' in content
        assert "set /a BACKUP_FAILED+=1" in content
        assert 'set "CLUTCHG_BACKUP_READY=0"' in content
        assert 'set "CLUTCHG_BACKUP_READY=1"' in content

    def test_registry_target_matrix_matches_compiled_restore_bindings(self):
        backup = _read(BACKUP)
        rollback = _read(ROLLBACK)
        capture_block = _section(backup, "backup_registry", "backup_registry_value")
        binding_block = _section(rollback, "bind_registry_component", "restore_services")

        assert set(VALUE_TARGETS) == set(VALUE_COMPONENTS)
        for component, (key, value) in VALUE_TARGETS.items():
            assert (
                f'call :backup_registry_value "{component}" "{key}" "{value}"'
                in capture_block
            )
            expected_binding = (
                f'if /i "%~1"=="{component}" (\n'
                f'    set "REGISTRY_KEY={key}"\n'
                f'    set "REGISTRY_VALUE={value}"\n'
                "    exit /b 0\n"
                ")"
            )
            assert expected_binding in binding_block

    def test_service_capture_inventory_matches_restore_inventory(self):
        backup = _read(BACKUP)
        rollback = _read(ROLLBACK)
        expected = " ".join(SERVICE_NAMES)

        assert f"for %%S in ({expected}) do call :backup_one_service" in backup
        assert f"for %%S in ({expected}) do call :restore_one_service" in rollback

    def test_plan_mode_is_non_mutating_branch_for_each_capture_type(self):
        content = _read(BACKUP)

        assert 'if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"' in content
        assert 'if /i "%~2"=="--plan" set "PLAN_MODE=1"' in content
        for marker in (
            "PLAN^|BACKUP^|registry-value",
            "PLAN^|BACKUP^|service",
            "PLAN^|BACKUP^|bcdedit /export",
            "PLAN^|QUERY^|powercfg /getactivescheme",
            "PLAN^|BACKUP^|powercfg /export",
            "PLAN^|BACKUP^|systeminfo",
        ):
            assert marker in content

    def test_registry_value_artifacts_are_canonical_state_only(self):
        content = _read(BACKUP)
        block = _section(content, "backup_registry_value", "record_all_registry_values_failed")

        for field in ("key_existed", "value_existed", "data"):
            assert f"echo {field}=" in block
        for forbidden in ("echo key=", "echo value=", "echo type="):
            assert forbidden not in block
        assert 'set "VALUE_FOUND=1"' in block
        assert 'if "!VALUE_FOUND!"=="1" if /i not "!VALUE_TYPE!"=="REG_DWORD" (' in block
        assert 'call :record_result "!COMPONENT_ID!" 1 "!ARTIFACT!"' in block
        assert 'set "ARTIFACT=registry-values\\!COMPONENT_ID!.state"' in block
        assert 'call :record_result "!COMPONENT_ID!" !ERRORLEVEL!' in block

    def test_active_power_scheme_is_exported_with_required_guid(self):
        content = _read(BACKUP)

        assert "powercfg /getactivescheme" in content
        assert r'powercfg /export "!BACKUP_FOLDER!\power_plan.pow" "!ACTIVE_POWER_GUID!"' in content
        assert r'>"!BACKUP_FOLDER!\active_power_guid.txt" echo !ACTIVE_POWER_GUID!' in content
        assert r'powercfg /export "!BACKUP_FOLDER!\power_plan.pow" >' not in content


@pytest.mark.unit
class TestRollbackContract:
    def test_restore_accepts_only_enumerated_contained_leaf_ids(self):
        content = _read(ROLLBACK)

        assert "\n:validate_backup_id\n" in content
        assert 'findstr /r /x "[0-9][0-9][0-9][0-9]-' in content
        assert r'for /d %%D in ("!BACKUPS_ROOT!\*")' in content
        assert 'if /i "%%~nxD"=="%~1"' in content
        assert r'for %%D in ("!RESTORE_DIR!\..")' in content
        assert "Backup path escaped the configured root" in content
        assert "Reparse-point backup leaves are not allowed" in content
        assert "Reparse points inside a backup are not allowed" in content

    def test_only_committed_complete_journals_are_restorable(self):
        content = _read(ROLLBACK)

        assert 'findstr /x /c:"format=clutchg-backup-v1"' in content
        assert 'findstr /x /c:"backup_id=!BACKUP_ID!"' in content
        assert 'findstr /x /c:"state=COMMITTED"' in content
        assert 'findstr /b /c:"END|COMMITTED|"' in content
        assert 'findstr /b /c:"RESULT|%%C|SUCCESS|"' in content
        assert "for %%C in (" + " ".join(COMPONENTS) + ")" in content

    def test_full_restore_uses_exact_value_components(self):
        content = _read(ROLLBACK)

        for component in VALUE_COMPONENTS:
            assert f'call :restore_registry_value "{component}"' in content
        for call in (
            "call :restore_services",
            "call :restore_bcd_component",
            "call :restore_power_scheme",
            "call :restore_system_info_component",
        ):
            assert call in content
        journaled_restore = _section(content, "restore_from_backup", "validate_backup_id")
        assert "restore_registry_component" not in content
        assert "reg import" not in journaled_restore
        assert "restore_registry BACKUP_ID COMPONENT_ID" in content

    def test_legacy_backups_use_only_the_fixed_historical_allowlist(self):
        content = _read(ROLLBACK)
        validation = _section(content, "validate_legacy_backup", "restore_legacy_backup")
        restore = _section(content, "restore_legacy_backup", "restore_registry_value")
        registry_files = (
            "multimedia.reg priority.reg desktop.reg telemetry.reg "
            "gamebar.reg contentdelivery.reg"
        )

        assert 'set "BACKUP_FORMAT=legacy"' in validation
        assert "LEGACY_UNAUTHENTICATED" in validation
        assert f"for %%F in ({registry_files} bcd_backup power_plan.pow)" in validation
        assert f"for %%F in ({registry_files}) do (" in restore
        assert 'reg import "!RESTORE_DIR!\\%%F"' in restore
        assert "*.reg" not in validation + restore
        assert "restore_legacy_registry_file" not in content
        assert "Targeted component restore is unavailable for legacy backups" in content

    def test_exact_value_restore_handles_present_and_absent_values(self):
        content = _read(ROLLBACK)
        restore_block = _section(content, "restore_registry_value", "restore_services")

        assert 'if "!VALUE_EXISTED!"=="1"' in restore_block
        assert 'reg add "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!"' in restore_block
        assert 'reg delete "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /f' in restore_block
        assert 'if "!KEY_EXISTED!"=="0" (' in restore_block
        assert 'reg delete "!REGISTRY_KEY!" /f' in restore_block

    def test_restore_aggregates_results_and_returns_nonzero_on_failure(self):
        content = _read(ROLLBACK)

        assert "set /a RESTORE_FAILED+=1" in content
        assert "if !RESTORE_FAILED! EQU 0" in content
        assert 'set "RETURN_CODE=1"' in content
        assert "exit /b !RETURN_CODE!" in content
        assert "if !RESTORE_FAILED! GTR 0 exit /b 1" in content
        assert "RESULT^|!RESULT_COMPONENT!^|FAILED^|exit=!RESULT_CODE!" in content

    def test_service_restore_uses_recorded_start_and_running_state(self):
        content = _read(ROLLBACK)

        assert 'for /f "usebackq tokens=1,2 delims=="' in content
        assert 'if /i "%%K"=="start_type"' in content
        assert 'if /i "%%K"=="delayed_auto"' in content
        assert 'if /i "%%K"=="running"' in content
        assert 'sc config "!SERVICE_NAME!" start= !SERVICE_START_ARG!' in content
        assert 'sc start "!SERVICE_NAME!"' in content
        assert 'sc stop "!SERVICE_NAME!"' in content

    def test_power_restore_reactivates_recorded_original_guid(self):
        content = _read(ROLLBACK)
        restore_block = _section(
            content, "restore_power_scheme", "restore_system_info_component"
        )

        assert r'set /p ORIGINAL_POWER_GUID=<"!RESTORE_DIR!\active_power_guid.txt"' in restore_block
        assert 'powercfg /setactive "!ORIGINAL_POWER_GUID!"' in restore_block
        assert "[guid]::NewGuid().ToString()" not in restore_block
        assert "powercfg /import" not in restore_block

    def test_single_component_restore_uses_exact_value_allowlist(self):
        content = _read(ROLLBACK)
        single_block = _section(content, "restore_registry", "record_restore_result")

        assert "& goto" not in single_block
        assert 'set "COMPONENT_ALLOWED=0"' in single_block
        assert f"for %%C in ({' '.join(VALUE_COMPONENTS)}) do (" in single_block
        assert 'if /i "!SINGLE_COMPONENT!"=="%%C" set "COMPONENT_ALLOWED=1"' in single_block
        assert 'if not "!COMPONENT_ALLOWED!"=="1"' in single_block
        assert 'call :restore_registry_value "!SINGLE_COMPONENT!"' in single_block
        assert r'set "RESTORE_JOURNAL=!RESTORE_DIR!\restore-journal.log"' in single_block

    def test_system_info_is_journaled_as_reference_not_as_restored_state(self):
        """A diagnostic capture must not be counted as recovered state.

        ``systeminfo.txt`` is a reference dump with nothing to write back. Calling
        ``record_restore_result`` for it would increment RESTORE_SUCCESS and make
        the restore journal claim one more component recovered than the engine
        actually recovered — the same overstatement class this audit exists to
        remove, inside the safety engine itself.
        """
        content = _read(ROLLBACK)
        block = _section(content, "restore_system_info_component", "restore_bcd")

        assert "REFERENCE_ONLY" in block
        assert "REFERENCE_MISSING" in block
        assert 'call :record_restore_result "system_info"' not in block

    def test_backup_journal_verification_is_unaffected_by_restore_journal(self):
        """The two journals are distinct files and must not be conflated.

        Backup validation requires RESULT|system_info|SUCCESS in ``journal.log``
        (the capture genuinely succeeded). The restore path writes to
        ``restore-journal.log``. Conflating them would either weaken backup
        validation or resurrect the overstatement.
        """
        content = _read(ROLLBACK)

        assert 'findstr /b /c:"RESULT|%%C|SUCCESS|" "!RESTORE_DIR!\\journal.log"' in content
        assert r'set "RESTORE_JOURNAL=!RESTORE_DIR!\restore-journal.log"' in content


@pytest.mark.unit
class TestFlightRecorderAndWrappers:
    def test_flight_recorder_supports_colon_and_plain_command_aliases(self):
        content = _read(FLIGHT_RECORDER)

        for command in (
            "create_registry_snapshot",
            "create_snapshot",
            "create_restore_point",
            "restore_registry_snapshot",
            "restore_snapshot",
            "list_snapshots",
        ):
            assert f'"==":{command}"' in content
            assert f'"=="{command}"' in content
        assert 'backup-registry.bat" create_backup' in content
        assert 'rollback.bat" restore_from_backup' in content
        assert "Partial registry capture is not a restorable transaction" in content
        assert "\n:usage_error\n" in content
        assert "exit /b 2" in content

    def test_flight_recorder_lists_only_committed_timestamp_leaf_ids(self):
        content = _read(FLIGHT_RECORDER)

        assert r'for /d %%D in ("!BACKUPS_ROOT!\*")' in content
        assert "findstr /r /x" in content
        assert 'findstr /x /c:"backup_id=!CANDIDATE_ID!"' in content
        assert 'findstr /x /c:"state=COMMITTED"' in content
        assert 'findstr /b /c:"END|COMMITTED|"' in content

    def test_extreme_rollback_delegates_to_exact_backup_restore(self):
        content = _read(EXTREME_ROLLBACK)

        assert 'rollback.bat" restore_from_backup "%BACKUP_ID%"' in content
        for forbidden in (
            "reg add ",
            "reg delete ",
            "bcdedit /deletevalue",
            "powercfg /setactive 381b",
        ):
            assert forbidden not in content.lower()

    def test_restore_point_has_plan_mode_and_no_implicit_enable(self):
        content = _read(RESTORE_POINT)
        create_block = _section(content, "create_restore_point", "enable_system_restore")

        assert "CLUTCHG_DRY_RUN" in content
        assert "--plan" in content
        assert "PLAN^|MUTATE^|powershell" in create_block
        assert "It is not enabled implicitly" in create_block
        assert "Enable-ComputerRestore" not in create_block
        assert "endlocal & exit /b 1" in create_block
