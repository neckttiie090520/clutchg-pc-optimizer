@echo off
:: ============================================================================
:: ClutchG Journaled Rollback Module
:: ============================================================================
:: Restores only a committed backup selected by exact enumerated leaf ID.
:: Set CLUTCHG_DRY_RUN=1 or pass --plan to validate and print without mutation.
:: ============================================================================

setlocal EnableExtensions EnableDelayedExpansion
set "COMMAND=%~1"
set "PLAN_MODE=0"
if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"
if /i "%~2"=="--plan" set "PLAN_MODE=1"
if /i "%~3"=="--plan" set "PLAN_MODE=1"
if /i "%~4"=="--plan" set "PLAN_MODE=1"

if /i "%COMMAND%"==":restore_from_backup" goto :dispatch_restore_all
if /i "%COMMAND%"=="restore_from_backup" goto :dispatch_restore_all
if /i "%COMMAND%"==":restore_bcd" goto :dispatch_restore_bcd
if /i "%COMMAND%"=="restore_bcd" goto :dispatch_restore_bcd
if /i "%COMMAND%"==":restore_registry" goto :dispatch_restore_registry
if /i "%COMMAND%"=="restore_registry" goto :dispatch_restore_registry
if not defined COMMAND goto :usage

echo ERROR: Unknown rollback command: %COMMAND%
goto :usage_error

:dispatch_restore_all
call :restore_from_backup "%~2"
goto :dispatch_done

:dispatch_restore_bcd
call :restore_bcd "%~2"
goto :dispatch_done

:dispatch_restore_registry
call :restore_registry "%~2" "%~3"
goto :dispatch_done

:dispatch_done
set "RETURN_CODE=!ERRORLEVEL!"
for %%R in (!RETURN_CODE!) do endlocal & exit /b %%R

:usage
echo Usage: rollback.bat restore_from_backup BACKUP_ID [--plan]
echo        rollback.bat restore_registry BACKUP_ID COMPONENT_ID [--plan]
endlocal & exit /b 0

:usage_error
echo Usage: rollback.bat restore_from_backup BACKUP_ID [--plan]
endlocal & exit /b 2

:restore_from_backup
set "REQUESTED_BACKUP_ID=%~1"
call :validate_backup_id "!REQUESTED_BACKUP_ID!"
if errorlevel 1 exit /b 2
call :resolve_backup_id "!REQUESTED_BACKUP_ID!"
if errorlevel 1 exit /b 2
call :validate_committed_backup
if errorlevel 1 exit /b 1
if /i "!BACKUP_FORMAT!"=="legacy" (
    call :restore_legacy_backup
    exit /b !ERRORLEVEL!
)

set /a RESTORE_SUCCESS=0
set /a RESTORE_FAILED=0
set "RESTORE_JOURNAL=!RESTORE_DIR!\restore-journal.log"
if "!PLAN_MODE!"=="1" (
    echo PLAN^|BEGIN_RESTORE^|backup_id=!BACKUP_ID!^|path=!RESTORE_DIR!
) else (
    >>"!RESTORE_JOURNAL!" echo BEGIN^|!BACKUP_ID!^|%DATE% %TIME%
)

call :restore_registry_value "value_gameconfig_dvr"
call :restore_registry_value "value_policy_gamedvr"
call :restore_registry_value "value_policy_allowgamedvr"
call :restore_registry_value "value_machine_gamedvr"
call :restore_registry_value "value_user_gamedvr"
call :restore_registry_value "value_gamebar_nexus"
call :restore_registry_value "value_gamebar_startup"
call :restore_registry_value "value_presencewriter_activation"
call :restore_registry_value "value_gamebar_allowgamemode"
call :restore_registry_value "value_gamebar_automode"
call :restore_registry_value "value_copilot_hkcu"
call :restore_registry_value "value_copilot_hklm"
call :restore_registry_value "value_windowsai_hkcu"
call :restore_registry_value "value_windowsai_hklm"
call :restore_registry_value "value_copilot_button"
call :restore_services
call :restore_bcd_component
call :restore_power_scheme
call :restore_system_info_component

if !RESTORE_FAILED! EQU 0 (
    set "FINAL_STATE=COMPLETED"
    set "RETURN_CODE=0"
) else (
    set "FINAL_STATE=FAILED"
    set "RETURN_CODE=1"
)
if "!PLAN_MODE!"=="1" (
    echo PLAN^|END_RESTORE^|state=!FINAL_STATE!^|success=!RESTORE_SUCCESS!^|failed=!RESTORE_FAILED!
) else (
    >>"!RESTORE_JOURNAL!" echo END^|!FINAL_STATE!^|success=!RESTORE_SUCCESS!^|failed=!RESTORE_FAILED!^|%DATE% %TIME%
)
if !RETURN_CODE! EQU 0 (
    echo Restore completed for !BACKUP_ID!. A restart is required.
) else (
    echo ERROR: Restore finished with !RESTORE_FAILED! component error^(s^).
)
exit /b !RETURN_CODE!

:validate_backup_id
set "CANDIDATE_BACKUP_ID=%~1"
if not defined CANDIDATE_BACKUP_ID (
    echo ERROR: A backup leaf ID is required.
    exit /b 1
)
echo(!CANDIDATE_BACKUP_ID!| findstr /r /x "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]-[0-9][0-9]-[0-9][0-9]" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backup ID must be a timestamp-shaped leaf ID.
    exit /b 1
)
exit /b 0

:resolve_backup_id
if defined BACKUPS_DIR (
    for %%D in ("%BACKUPS_DIR%") do set "BACKUPS_ROOT=%%~fD"
) else (
    for %%D in ("%~dp0..\backups") do set "BACKUPS_ROOT=%%~fD"
)
set "BACKUP_ID="
set "RESTORE_DIR="
if not exist "!BACKUPS_ROOT!" (
    echo ERROR: Backups root not found: !BACKUPS_ROOT!
    exit /b 1
)
for /d %%D in ("!BACKUPS_ROOT!\*") do (
    if /i "%%~nxD"=="%~1" (
        set "BACKUP_ID=%%~nxD"
        set "RESTORE_DIR=%%~fD"
    )
)
if not defined RESTORE_DIR (
    echo ERROR: Backup ID is not an enumerated leaf under the backups root: %~1
    exit /b 1
)
for %%D in ("!RESTORE_DIR!\..") do if /i not "%%~fD"=="!BACKUPS_ROOT!" (
    echo ERROR: Backup path escaped the configured root.
    set "BACKUP_ID="
    set "RESTORE_DIR="
    exit /b 1
)
for %%D in ("!RESTORE_DIR!") do set "RESTORE_ATTRIBUTES=%%~aD"
echo(!RESTORE_ATTRIBUTES!| findstr /i "l" >nul 2>&1
if not errorlevel 1 (
    echo ERROR: Reparse-point backup leaves are not allowed.
    set "BACKUP_ID="
    set "RESTORE_DIR="
    exit /b 1
)
exit /b 0

:validate_committed_backup
set "MANIFEST=!RESTORE_DIR!\manifest.ini"
set "BACKUP_FORMAT=journaled"
if not exist "!MANIFEST!" (
    call :validate_legacy_backup
    exit /b !ERRORLEVEL!
)
findstr /x /c:"format=clutchg-backup-v1" "!MANIFEST!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Unsupported backup manifest format.
    exit /b 1
)
findstr /x /c:"backup_id=!BACKUP_ID!" "!MANIFEST!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Manifest backup ID does not match its leaf directory.
    exit /b 1
)
findstr /x /c:"state=COMMITTED" "!MANIFEST!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backup transaction is not committed.
    exit /b 1
)
findstr /x /c:"components=value_gameconfig_dvr,value_policy_gamedvr,value_policy_allowgamedvr,value_machine_gamedvr,value_user_gamedvr,value_gamebar_nexus,value_gamebar_startup,value_presencewriter_activation,value_gamebar_allowgamemode,value_gamebar_automode,value_copilot_hkcu,value_copilot_hklm,value_windowsai_hkcu,value_windowsai_hklm,value_copilot_button,services,bcd,power_scheme,system_info" "!MANIFEST!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Manifest component contract is incomplete or unknown.
    exit /b 1
)
for %%C in (value_gameconfig_dvr value_policy_gamedvr value_policy_allowgamedvr value_machine_gamedvr value_user_gamedvr value_gamebar_nexus value_gamebar_startup value_presencewriter_activation value_gamebar_allowgamemode value_gamebar_automode value_copilot_hkcu value_copilot_hklm value_windowsai_hkcu value_windowsai_hklm value_copilot_button) do (
    if not exist "!RESTORE_DIR!\registry-values\%%C.state" (
        echo ERROR: Missing registry value artifact: %%C
        exit /b 1
    )
)
if not exist "!RESTORE_DIR!\journal.log" (
    echo ERROR: Backup has no transaction journal.
    exit /b 1
)
findstr /b /c:"END|COMMITTED|" "!RESTORE_DIR!\journal.log" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backup journal has no committed transaction record.
    exit /b 1
)
for %%C in (value_gameconfig_dvr value_policy_gamedvr value_policy_allowgamedvr value_machine_gamedvr value_user_gamedvr value_gamebar_nexus value_gamebar_startup value_presencewriter_activation value_gamebar_allowgamemode value_gamebar_automode value_copilot_hkcu value_copilot_hklm value_windowsai_hkcu value_windowsai_hklm value_copilot_button services bcd power_scheme system_info) do (
    findstr /b /c:"RESULT|%%C|SUCCESS|" "!RESTORE_DIR!\journal.log" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Backup journal has no successful result for component %%C.
        exit /b 1
    )
)
set "REPARSE_CHILD="
for /f "delims=" %%L in ('dir /al /s /b "!RESTORE_DIR!" 2^>nul') do set "REPARSE_CHILD=%%L"
if defined REPARSE_CHILD (
    echo ERROR: Reparse points inside a backup are not allowed.
    exit /b 1
)
if not exist "!RESTORE_DIR!\services" (
    echo ERROR: Missing services artifact.
    exit /b 1
)
if not exist "!RESTORE_DIR!\bcd_backup" (
    echo ERROR: Missing BCD artifact.
    exit /b 1
)
if not exist "!RESTORE_DIR!\power_plan.pow" (
    echo ERROR: Missing power scheme artifact.
    exit /b 1
)
if not exist "!RESTORE_DIR!\active_power_guid.txt" (
    echo ERROR: Missing active power GUID artifact.
    exit /b 1
)
if not exist "!RESTORE_DIR!\systeminfo.txt" (
    echo ERROR: Missing system information artifact.
    exit /b 1
)
exit /b 0

:validate_legacy_backup
set "BACKUP_FORMAT=legacy"
set /a LEGACY_ARTIFACTS=0
for %%F in (multimedia.reg priority.reg desktop.reg telemetry.reg gamebar.reg contentdelivery.reg bcd_backup power_plan.pow) do (
    if exist "!RESTORE_DIR!\%%F" set /a LEGACY_ARTIFACTS+=1
)
if !LEGACY_ARTIFACTS! EQU 0 (
    echo ERROR: Legacy backup has no recognized recovery artifacts.
    exit /b 1
)
set "REPARSE_CHILD="
for /f "delims=" %%L in ('dir /al /s /b "!RESTORE_DIR!" 2^>nul') do set "REPARSE_CHILD=%%L"
if defined REPARSE_CHILD (
    echo ERROR: Reparse points inside a backup are not allowed.
    exit /b 1
)
echo WARNING: LEGACY_UNAUTHENTICATED backup; restoring only known legacy artifacts.
exit /b 0

:restore_legacy_backup
set /a LEGACY_RESTORED=0
set /a LEGACY_FAILED=0
for %%F in (multimedia.reg priority.reg desktop.reg telemetry.reg gamebar.reg contentdelivery.reg) do (
    if exist "!RESTORE_DIR!\%%F" (
        if "!PLAN_MODE!"=="1" (
            echo PLAN^|RESTORE^|legacy-registry^|reg import "!RESTORE_DIR!\%%F"
            set /a LEGACY_RESTORED+=1
        ) else (
            reg import "!RESTORE_DIR!\%%F" >nul 2>&1
            if errorlevel 1 (
                set /a LEGACY_FAILED+=1
            ) else (
                set /a LEGACY_RESTORED+=1
            )
        )
    )
)
if exist "!RESTORE_DIR!\bcd_backup" (
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESTORE^|legacy-bcd^|bcdedit /import "!RESTORE_DIR!\bcd_backup"
        set /a LEGACY_RESTORED+=1
    ) else (
        bcdedit /import "!RESTORE_DIR!\bcd_backup" >nul 2>&1
        if errorlevel 1 (
            set /a LEGACY_FAILED+=1
        ) else (
            set /a LEGACY_RESTORED+=1
        )
    )
)
if exist "!RESTORE_DIR!\power_plan.pow" (
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESTORE^|legacy-power^|powercfg /import "!RESTORE_DIR!\power_plan.pow"
        set /a LEGACY_RESTORED+=1
    ) else (
        powercfg /import "!RESTORE_DIR!\power_plan.pow" >nul 2>&1
        if errorlevel 1 (
            set /a LEGACY_FAILED+=1
        ) else (
            set /a LEGACY_RESTORED+=1
        )
    )
)
if !LEGACY_FAILED! GTR 0 (
    echo ERROR: Legacy restore failed for !LEGACY_FAILED! artifacts.
    exit /b 1
)
echo Legacy restore completed for !LEGACY_RESTORED! recognized artifacts. A restart is required.
exit /b 0

:restore_registry_value
set "COMPONENT_ID=%~1"
set "STATE_FILE=!RESTORE_DIR!\registry-values\!COMPONENT_ID!.state"
if not exist "!STATE_FILE!" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
set "REGISTRY_KEY="
set "REGISTRY_VALUE="
call :bind_registry_component "!COMPONENT_ID!"
if errorlevel 1 (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
set "KEY_EXISTED="
set "VALUE_EXISTED="
set "VALUE_DATA="
set "STATE_LINE_COUNT="
set /a KEY_STATE_LINES=0
set /a VALUE_STATE_LINES=0
set /a DATA_STATE_LINES=0
:: %SystemRoot%\System32 is qualified deliberately: a bare "find" resolves to
:: GNU find when Git Bash or similar is on PATH, which takes different switches
:: and scans the filesystem instead of counting lines — the restore then hangs.
for /f %%N in ('%SystemRoot%\System32\find.exe /v /c "" ^< "!STATE_FILE!"') do set "STATE_LINE_COUNT=%%N"
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"key_existed=[01]" "!STATE_FILE!" 2^>nul') do (
    set /a KEY_STATE_LINES+=1
    set "KEY_EXISTED=%%B"
)
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"value_existed=[01]" "!STATE_FILE!" 2^>nul') do (
    set /a VALUE_STATE_LINES+=1
    set "VALUE_EXISTED=%%B"
)
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"data=" /c:"data=0x[0-9A-Fa-f][0-9A-Fa-f]*" "!STATE_FILE!" 2^>nul') do (
    set /a DATA_STATE_LINES+=1
    set "VALUE_DATA=%%B"
)
if not "!STATE_LINE_COUNT!"=="3" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if not "!KEY_STATE_LINES!"=="1" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if not "!VALUE_STATE_LINES!"=="1" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if not "!DATA_STATE_LINES!"=="1" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if "!KEY_EXISTED!"=="0" if "!VALUE_EXISTED!"=="1" (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if "!VALUE_EXISTED!"=="1" if not defined VALUE_DATA (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if "!VALUE_EXISTED!"=="0" if defined VALUE_DATA (
    call :record_restore_result "!COMPONENT_ID!" 1
    exit /b 0
)
if "!PLAN_MODE!"=="1" (
    echo PLAN^|RESTORE^|!COMPONENT_ID!^|key_existed=!KEY_EXISTED!^|value_existed=!VALUE_EXISTED!
    call :record_restore_result "!COMPONENT_ID!" 0
    exit /b 0
)
if "!VALUE_EXISTED!"=="1" (
    reg add "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /t REG_DWORD /d "!VALUE_DATA!" /f >nul 2>&1
    call :record_restore_result "!COMPONENT_ID!" !ERRORLEVEL!
    exit /b 0
)
if "!KEY_EXISTED!"=="0" (
    reg delete "!REGISTRY_KEY!" /f >nul 2>&1
    reg query "!REGISTRY_KEY!" >nul 2>&1 && set "DELETE_CODE=1" || set "DELETE_CODE=0"
) else (
    reg delete "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /f >nul 2>&1
    reg query "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" >nul 2>&1 && set "DELETE_CODE=1" || set "DELETE_CODE=0"
)
call :record_restore_result "!COMPONENT_ID!" !DELETE_CODE!
exit /b 0

:bind_registry_component
if /i "%~1"=="value_gameconfig_dvr" (
    set "REGISTRY_KEY=HKCU\System\GameConfigStore"
    set "REGISTRY_VALUE=GameDVR_Enabled"
    exit /b 0
)
if /i "%~1"=="value_policy_gamedvr" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
    set "REGISTRY_VALUE=AllowGameDVR"
    exit /b 0
)
if /i "%~1"=="value_policy_allowgamedvr" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR"
    set "REGISTRY_VALUE=value"
    exit /b 0
)
if /i "%~1"=="value_machine_gamedvr" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"
    set "REGISTRY_VALUE=AppCaptureEnabled"
    exit /b 0
)
if /i "%~1"=="value_user_gamedvr" (
    set "REGISTRY_KEY=HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"
    set "REGISTRY_VALUE=AppCaptureEnabled"
    exit /b 0
)
if /i "%~1"=="value_gamebar_nexus" (
    set "REGISTRY_KEY=HKCU\Software\Microsoft\GameBar"
    set "REGISTRY_VALUE=UseNexusForGameBarEnabled"
    exit /b 0
)
if /i "%~1"=="value_gamebar_startup" (
    set "REGISTRY_KEY=HKCU\Software\Microsoft\GameBar"
    set "REGISTRY_VALUE=ShowStartupPanel"
    exit /b 0
)
if /i "%~1"=="value_presencewriter_activation" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter"
    set "REGISTRY_VALUE=ActivationType"
    exit /b 0
)
if /i "%~1"=="value_gamebar_allowgamemode" (
    set "REGISTRY_KEY=HKCU\Software\Microsoft\GameBar"
    set "REGISTRY_VALUE=AllowAutoGameMode"
    exit /b 0
)
if /i "%~1"=="value_gamebar_automode" (
    set "REGISTRY_KEY=HKCU\Software\Microsoft\GameBar"
    set "REGISTRY_VALUE=AutoGameModeEnabled"
    exit /b 0
)
if /i "%~1"=="value_copilot_hkcu" (
    set "REGISTRY_KEY=HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot"
    set "REGISTRY_VALUE=TurnOffWindowsCopilot"
    exit /b 0
)
if /i "%~1"=="value_copilot_hklm" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot"
    set "REGISTRY_VALUE=TurnOffWindowsCopilot"
    exit /b 0
)
if /i "%~1"=="value_windowsai_hkcu" (
    set "REGISTRY_KEY=HKCU\Software\Policies\Microsoft\Windows\WindowsAI"
    set "REGISTRY_VALUE=DisableAIDataAnalysis"
    exit /b 0
)
if /i "%~1"=="value_windowsai_hklm" (
    set "REGISTRY_KEY=HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI"
    set "REGISTRY_VALUE=DisableAIDataAnalysis"
    exit /b 0
)
if /i "%~1"=="value_copilot_button" (
    set "REGISTRY_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    set "REGISTRY_VALUE=ShowCopilotButton"
    exit /b 0
)
exit /b 1

:restore_services
set "SERVICE_RESTORE_FAILED=0"
for %%S in (DiagTrack dmwappushservice diagnosticshub.standardcollector.service SysMain WSearch XblAuthManager XblGameSave XboxNetApiSvc XboxGipSvc RetailDemo MapsBroker lfsvc SharedAccess Fax WFDSConMgrSvc TabletInputService Spooler SEMgrSvc RmSvc WalletService UsoSvc) do call :restore_one_service "%%S"
call :record_restore_result "services" !SERVICE_RESTORE_FAILED!
exit /b 0

:restore_one_service
set "SERVICE_NAME=%~1"
set "SERVICE_STATE_FILE=!RESTORE_DIR!\services\!SERVICE_NAME!.state"
if exist "!RESTORE_DIR!\services\!SERVICE_NAME!.absent" (
    if "!PLAN_MODE!"=="1" echo PLAN^|RESTORE^|service !SERVICE_NAME!^|originally-absent-no-action
    exit /b 0
)
if not exist "!SERVICE_STATE_FILE!" (
    set "SERVICE_RESTORE_FAILED=1"
    exit /b 0
)
set "SERVICE_START_TYPE="
set "SERVICE_DELAYED=0"
set "SERVICE_RUNNING=0"
for /f "usebackq tokens=1,2 delims==" %%K in ("!SERVICE_STATE_FILE!") do (
    if /i "%%K"=="start_type" set "SERVICE_START_TYPE=%%L"
    if /i "%%K"=="delayed_auto" set "SERVICE_DELAYED=%%L"
    if /i "%%K"=="running" set "SERVICE_RUNNING=%%L"
)
set "SERVICE_START_ARG="
if "!SERVICE_START_TYPE!"=="2" set "SERVICE_START_ARG=auto"
if "!SERVICE_START_TYPE!"=="3" set "SERVICE_START_ARG=demand"
if "!SERVICE_START_TYPE!"=="4" set "SERVICE_START_ARG=disabled"
if "!SERVICE_DELAYED!"=="1" if "!SERVICE_START_TYPE!"=="2" set "SERVICE_START_ARG=delayed-auto"
if not defined SERVICE_START_ARG (
    set "SERVICE_RESTORE_FAILED=1"
    exit /b 0
)
if "!PLAN_MODE!"=="1" (
    echo PLAN^|RESTORE^|service !SERVICE_NAME!^|sc config "!SERVICE_NAME!" start= !SERVICE_START_ARG!
    if "!SERVICE_RUNNING!"=="1" (
        echo PLAN^|RESTORE^|service !SERVICE_NAME!^|sc start "!SERVICE_NAME!"
    ) else (
        echo PLAN^|RESTORE^|service !SERVICE_NAME!^|sc stop "!SERVICE_NAME!"
    )
    exit /b 0
)
sc config "!SERVICE_NAME!" start= !SERVICE_START_ARG! >nul 2>&1
if errorlevel 1 set "SERVICE_RESTORE_FAILED=1"
if "!SERVICE_RUNNING!"=="1" (
    sc start "!SERVICE_NAME!" >nul 2>&1
    if errorlevel 1 (
        sc query "!SERVICE_NAME!" 2>nul | findstr /c:"RUNNING" >nul 2>&1
        if errorlevel 1 set "SERVICE_RESTORE_FAILED=1"
    )
) else (
    sc stop "!SERVICE_NAME!" >nul 2>&1
    sc query "!SERVICE_NAME!" 2>nul | findstr /c:"STOPPED" >nul 2>&1
    if errorlevel 1 set "SERVICE_RESTORE_FAILED=1"
)
exit /b 0

:restore_bcd_component
if "!PLAN_MODE!"=="1" (
    echo PLAN^|RESTORE^|bcd^|bcdedit /import "!RESTORE_DIR!\bcd_backup"
    call :record_restore_result "bcd" 0
    exit /b 0
)
bcdedit /import "!RESTORE_DIR!\bcd_backup" >nul 2>&1
call :record_restore_result "bcd" !ERRORLEVEL!
exit /b 0

:restore_power_scheme
set "ORIGINAL_POWER_GUID="
if "!PLAN_MODE!"=="1" (
    echo PLAN^|RESTORE^|power_scheme^|read "!RESTORE_DIR!\active_power_guid.txt"
    echo PLAN^|RESTORE^|power_scheme^|powercfg /setactive "{ORIGINAL_POWER_GUID}"
    call :record_restore_result "power_scheme" 0
    exit /b 0
)
set /p ORIGINAL_POWER_GUID=<"!RESTORE_DIR!\active_power_guid.txt"
for /f "tokens=*" %%G in ("!ORIGINAL_POWER_GUID!") do set "ORIGINAL_POWER_GUID=%%G"
echo(!ORIGINAL_POWER_GUID!| findstr /r /x "[0-9A-Fa-f][0-9A-Fa-f]*-[0-9A-Fa-f][0-9A-Fa-f]*-[0-9A-Fa-f][0-9A-Fa-f]*-[0-9A-Fa-f][0-9A-Fa-f]*-[0-9A-Fa-f][0-9A-Fa-f]*" >nul 2>&1
if errorlevel 1 (
    call :record_restore_result "power_scheme" 1
    exit /b 0
)
powercfg /setactive "!ORIGINAL_POWER_GUID!" >nul 2>&1
call :record_restore_result "power_scheme" !ERRORLEVEL!
exit /b 0

:restore_system_info_component
:: system_info is a diagnostic capture (systeminfo.txt), not restorable state.
:: It is verified present so the transaction is auditable, but it must not be
:: counted as a restored component: doing so would report more state recovered
:: than the engine actually recovered.
if "!PLAN_MODE!"=="1" (
    echo PLAN^|VERIFY^|system_info^|"!RESTORE_DIR!\systeminfo.txt"
    echo PLAN^|RESULT^|system_info^|REFERENCE_ONLY
    exit /b 0
)
if exist "!RESTORE_DIR!\systeminfo.txt" (
    >>"!RESTORE_JOURNAL!" echo RESULT^|system_info^|REFERENCE_ONLY
) else (
    >>"!RESTORE_JOURNAL!" echo RESULT^|system_info^|REFERENCE_MISSING
)
exit /b 0

:restore_bcd
call :restore_from_backup "%~1"
exit /b !ERRORLEVEL!

:restore_registry
set "SINGLE_BACKUP_ID=%~1"
set "SINGLE_COMPONENT=%~2"
if not defined SINGLE_COMPONENT (
    echo ERROR: An enumerated registry component ID is required.
    exit /b 2
)
call :validate_backup_id "!SINGLE_BACKUP_ID!"
if errorlevel 1 exit /b 2
call :resolve_backup_id "!SINGLE_BACKUP_ID!"
if errorlevel 1 exit /b 2
call :validate_committed_backup
if errorlevel 1 exit /b 1
if /i "!BACKUP_FORMAT!"=="legacy" (
    echo ERROR: Targeted component restore is unavailable for legacy backups; use restore_from_backup.
    exit /b 2
)
set /a RESTORE_SUCCESS=0
set /a RESTORE_FAILED=0
set "RESTORE_JOURNAL=!RESTORE_DIR!\restore-journal.log"
set "COMPONENT_ALLOWED=0"
for %%C in (value_gameconfig_dvr value_policy_gamedvr value_policy_allowgamedvr value_machine_gamedvr value_user_gamedvr value_gamebar_nexus value_gamebar_startup value_presencewriter_activation value_gamebar_allowgamemode value_gamebar_automode value_copilot_hkcu value_copilot_hklm value_windowsai_hkcu value_windowsai_hklm value_copilot_button) do (
    if /i "!SINGLE_COMPONENT!"=="%%C" set "COMPONENT_ALLOWED=1"
)
if not "!COMPONENT_ALLOWED!"=="1" (
    echo ERROR: Unknown registry value component ID: !SINGLE_COMPONENT!
    exit /b 2
)
call :restore_registry_value "!SINGLE_COMPONENT!"
if !RESTORE_FAILED! GTR 0 exit /b 1
exit /b 0

:record_restore_result
set "RESULT_COMPONENT=%~1"
set "RESULT_CODE=%~2"
if "!RESULT_CODE!"=="0" (
    set /a RESTORE_SUCCESS+=1
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESULT^|!RESULT_COMPONENT!^|SUCCESS
    ) else (
        >>"!RESTORE_JOURNAL!" echo RESULT^|!RESULT_COMPONENT!^|SUCCESS
    )
) else (
    set /a RESTORE_FAILED+=1
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESULT^|!RESULT_COMPONENT!^|FAILED^|exit=!RESULT_CODE!
    ) else (
        >>"!RESTORE_JOURNAL!" echo RESULT^|!RESULT_COMPONENT!^|FAILED^|exit=!RESULT_CODE!
    )
)
exit /b 0
