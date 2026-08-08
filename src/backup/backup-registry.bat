@echo off
:: ============================================================================
:: ClutchG Backup Transaction Module
:: ============================================================================
:: Creates a journaled backup before system mutation. A backup is restorable
:: only when manifest.ini ends in state=COMMITTED and every required component
:: was captured. Set CLUTCHG_DRY_RUN=1 or pass --plan to print the plan only.
:: ============================================================================

setlocal EnableExtensions EnableDelayedExpansion
set "COMMAND=%~1"
set "PLAN_MODE=0"
if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"
if /i "%~2"=="--plan" set "PLAN_MODE=1"
if /i "%~3"=="--plan" set "PLAN_MODE=1"

if /i "%COMMAND%"==":create_backup" goto :dispatch_create_backup
if /i "%COMMAND%"=="create_backup" goto :dispatch_create_backup
if /i "%COMMAND%"==":backup_registry" goto :dispatch_backup_registry
if /i "%COMMAND%"=="backup_registry" goto :dispatch_backup_registry
if /i "%COMMAND%"==":backup_services" goto :dispatch_backup_services
if /i "%COMMAND%"=="backup_services" goto :dispatch_backup_services
if not defined COMMAND goto :usage

echo ERROR: Unknown backup command: %COMMAND%
goto :usage_error

:dispatch_create_backup
call :create_backup
goto :dispatch_done

:dispatch_backup_registry
call :require_transaction_context
if errorlevel 1 goto :dispatch_done
call :backup_registry
goto :dispatch_done

:dispatch_backup_services
call :require_transaction_context
if errorlevel 1 goto :dispatch_done
call :backup_services
goto :dispatch_done

:dispatch_done
set "RETURN_CODE=!ERRORLEVEL!"
set "EXPORTED_BACKUP_FOLDER=!BACKUP_FOLDER!"
set "EXPORTED_BACKUP_ID=!BACKUP_ID!"
set "EXPORTED_BACKUP_READY=!CLUTCHG_BACKUP_READY!"
for %%R in (!RETURN_CODE!) do endlocal & set "BACKUP_FOLDER=%EXPORTED_BACKUP_FOLDER%" & set "BACKUP_ID=%EXPORTED_BACKUP_ID%" & set "CLUTCHG_BACKUP_READY=%EXPORTED_BACKUP_READY%" & exit /b %%R

:require_transaction_context
if defined BACKUP_FOLDER if defined JOURNAL exit /b 0
echo ERROR: Component backup commands require an active create_backup transaction.
exit /b 2

:usage
echo Usage: backup-registry.bat create_backup [--plan]
endlocal & exit /b 0

:usage_error
echo Usage: backup-registry.bat create_backup [--plan]
endlocal & exit /b 2

:create_backup
set "CLUTCHG_BACKUP_READY=0"
set /a BACKUP_SUCCESS=0
set /a BACKUP_FAILED=0

if defined BACKUPS_DIR (
    for %%D in ("%BACKUPS_DIR%") do set "BACKUPS_ROOT=%%~fD"
) else (
    for %%D in ("%~dp0..\backups") do set "BACKUPS_ROOT=%%~fD"
)

if "!PLAN_MODE!"=="1" (
    if defined CLUTCHG_PLAN_ID (
        set "BACKUP_ID=%CLUTCHG_PLAN_ID%"
    ) else (
        set "BACKUP_ID=2099-01-01_00-00-00"
    )
) else (
    for /f "tokens=*" %%T in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "BACKUP_ID=%%T"
    if not defined BACKUP_ID (
        echo ERROR: Could not generate backup ID.
        exit /b 1
    )
)

set "BACKUP_FOLDER=!BACKUPS_ROOT!\!BACKUP_ID!"
set "MANIFEST=!BACKUP_FOLDER!\manifest.ini"
set "JOURNAL=!BACKUP_FOLDER!\journal.log"

if "!PLAN_MODE!"=="1" (
    echo PLAN^|BEGIN^|backup_id=!BACKUP_ID!^|root=!BACKUPS_ROOT!
) else (
    if not exist "!BACKUPS_ROOT!" mkdir "!BACKUPS_ROOT!" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Could not create backup root: !BACKUPS_ROOT!
        exit /b 1
    )
    if exist "!BACKUP_FOLDER!" (
        echo ERROR: Backup ID already exists: !BACKUP_ID!
        exit /b 1
    )
    mkdir "!BACKUP_FOLDER!" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Could not create backup folder: !BACKUP_FOLDER!
        exit /b 1
    )
    call :write_manifest_header
    if errorlevel 1 exit /b 1
    >"!JOURNAL!" echo BEGIN^|!BACKUP_ID!^|%DATE% %TIME%
)

echo     Creating backup transaction: !BACKUP_ID!
echo     Backup root: !BACKUPS_ROOT!

call :backup_registry
call :backup_services
call :backup_bcd
call :backup_power_scheme
call :backup_system_info

if !BACKUP_FAILED! EQU 0 (
    set "FINAL_STATE=COMMITTED"
    set "CLUTCHG_BACKUP_READY=1"
    set "RETURN_CODE=0"
) else (
    set "FINAL_STATE=FAILED"
    set "CLUTCHG_BACKUP_READY=0"
    set "RETURN_CODE=1"
)

if "!PLAN_MODE!"=="1" (
    echo PLAN^|END^|state=!FINAL_STATE!^|success=!BACKUP_SUCCESS!^|failed=!BACKUP_FAILED!
) else (
    >>"!MANIFEST!" echo state=!FINAL_STATE!
    >>"!JOURNAL!" echo END^|!FINAL_STATE!^|success=!BACKUP_SUCCESS!^|failed=!BACKUP_FAILED!^|%DATE% %TIME%
    >"!BACKUP_FOLDER!\README.txt" echo ClutchG journaled backup
    >>"!BACKUP_FOLDER!\README.txt" echo Backup ID: !BACKUP_ID!
    >>"!BACKUP_FOLDER!\README.txt" echo State: !FINAL_STATE!
    >>"!BACKUP_FOLDER!\README.txt" echo Restore only through safety\rollback.bat using this leaf ID.
)

if !RETURN_CODE! EQU 0 (
    echo     Backup transaction committed: !BACKUP_ID!
) else (
    echo ERROR: Backup transaction failed with !BACKUP_FAILED! component error^(s^).
)
exit /b !RETURN_CODE!

:write_manifest_header
>"!MANIFEST!" echo format=clutchg-backup-v1
if errorlevel 1 exit /b 1
>>"!MANIFEST!" echo backup_id=!BACKUP_ID!
>>"!MANIFEST!" echo state=PREPARING
>>"!MANIFEST!" echo components=value_gameconfig_dvr,value_policy_gamedvr,value_policy_allowgamedvr,value_machine_gamedvr,value_user_gamedvr,value_gamebar_nexus,value_gamebar_startup,value_presencewriter_activation,value_gamebar_allowgamemode,value_gamebar_automode,value_copilot_hkcu,value_copilot_hklm,value_windowsai_hkcu,value_windowsai_hklm,value_copilot_button,services,bcd,power_scheme,system_info
>>"!MANIFEST!" echo registry_values=registry-values
>>"!MANIFEST!" echo services=services
>>"!MANIFEST!" echo bcd=bcd_backup
>>"!MANIFEST!" echo power_scheme=power_plan.pow
>>"!MANIFEST!" echo power_guid=active_power_guid.txt
>>"!MANIFEST!" echo system_info=systeminfo.txt
exit /b 0

:backup_registry
echo     Backing up exact registry value state...
if "!PLAN_MODE!"=="0" (
    if not exist "!BACKUP_FOLDER!\registry-values" mkdir "!BACKUP_FOLDER!\registry-values" >nul 2>&1
    if errorlevel 1 (
        call :record_all_registry_values_failed
        exit /b 0
    )
)
call :backup_registry_value "value_gameconfig_dvr" "HKCU\System\GameConfigStore" "GameDVR_Enabled"
call :backup_registry_value "value_policy_gamedvr" "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" "AllowGameDVR"
call :backup_registry_value "value_policy_allowgamedvr" "HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" "value"
call :backup_registry_value "value_machine_gamedvr" "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled"
call :backup_registry_value "value_user_gamedvr" "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled"
call :backup_registry_value "value_gamebar_nexus" "HKCU\Software\Microsoft\GameBar" "UseNexusForGameBarEnabled"
call :backup_registry_value "value_gamebar_startup" "HKCU\Software\Microsoft\GameBar" "ShowStartupPanel"
call :backup_registry_value "value_presencewriter_activation" "HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter" "ActivationType"
call :backup_registry_value "value_gamebar_allowgamemode" "HKCU\Software\Microsoft\GameBar" "AllowAutoGameMode"
call :backup_registry_value "value_gamebar_automode" "HKCU\Software\Microsoft\GameBar" "AutoGameModeEnabled"
call :backup_registry_value "value_copilot_hkcu" "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" "TurnOffWindowsCopilot"
call :backup_registry_value "value_copilot_hklm" "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" "TurnOffWindowsCopilot"
call :backup_registry_value "value_windowsai_hkcu" "HKCU\Software\Policies\Microsoft\Windows\WindowsAI" "DisableAIDataAnalysis"
call :backup_registry_value "value_windowsai_hklm" "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" "DisableAIDataAnalysis"
call :backup_registry_value "value_copilot_button" "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "ShowCopilotButton"
exit /b 0

:backup_registry_value
set "COMPONENT_ID=%~1"
set "REGISTRY_KEY=%~2"
set "REGISTRY_VALUE=%~3"
set "ARTIFACT=registry-values\!COMPONENT_ID!.state"
if "!PLAN_MODE!"=="1" (
    echo PLAN^|BACKUP^|registry-value !REGISTRY_KEY!\!REGISTRY_VALUE!
    call :record_result "!COMPONENT_ID!" 0 "!ARTIFACT!"
    exit /b 0
)
set "KEY_EXISTED=0"
set "VALUE_FOUND=0"
set "VALUE_EXISTED=0"
set "VALUE_TYPE="
set "VALUE_DATA="
reg query "!REGISTRY_KEY!" >nul 2>&1 && set "KEY_EXISTED=1"
for /f "skip=2 tokens=1,2,*" %%A in ('reg query "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" 2^>nul') do (
    if /i "%%A"=="!REGISTRY_VALUE!" (
        set "VALUE_FOUND=1"
        set "VALUE_TYPE=%%B"
        set "VALUE_DATA=%%C"
    )
)
if "!VALUE_FOUND!"=="1" if /i not "!VALUE_TYPE!"=="REG_DWORD" (
    call :record_result "!COMPONENT_ID!" 1 "!ARTIFACT!"
    exit /b 0
)
if "!VALUE_FOUND!"=="1" set "VALUE_EXISTED=1"
>"!BACKUP_FOLDER!\!ARTIFACT!" echo key_existed=!KEY_EXISTED!
>>"!BACKUP_FOLDER!\!ARTIFACT!" echo value_existed=!VALUE_EXISTED!
>>"!BACKUP_FOLDER!\!ARTIFACT!" echo data=!VALUE_DATA!
call :record_result "!COMPONENT_ID!" !ERRORLEVEL! "!ARTIFACT!"
exit /b 0

:record_all_registry_values_failed
for %%C in (value_gameconfig_dvr value_policy_gamedvr value_policy_allowgamedvr value_machine_gamedvr value_user_gamedvr value_gamebar_nexus value_gamebar_startup value_presencewriter_activation value_gamebar_allowgamemode value_gamebar_automode value_copilot_hkcu value_copilot_hklm value_windowsai_hkcu value_windowsai_hklm value_copilot_button) do call :record_result "%%C" 1 "registry-values\%%C.state"
exit /b 0

:backup_services
echo     Backing up service configuration and running state...
if "!PLAN_MODE!"=="0" (
    if not exist "!BACKUP_FOLDER!\services" mkdir "!BACKUP_FOLDER!\services" >nul 2>&1
    if errorlevel 1 (
        call :record_result "services" 1 "services"
        exit /b 0
    )
) else (
    echo PLAN^|MKDIR^|"!BACKUP_FOLDER!\services"
)
set "SERVICE_CAPTURE_FAILED=0"
for %%S in (DiagTrack dmwappushservice diagnosticshub.standardcollector.service SysMain WSearch XblAuthManager XblGameSave XboxNetApiSvc XboxGipSvc RetailDemo MapsBroker lfsvc SharedAccess Fax WFDSConMgrSvc TabletInputService Spooler SEMgrSvc RmSvc WalletService UsoSvc) do call :backup_one_service "%%S"
call :record_result "services" !SERVICE_CAPTURE_FAILED! "services"
exit /b 0

:backup_one_service
set "SERVICE_NAME=%~1"
if "!PLAN_MODE!"=="1" (
    echo PLAN^|BACKUP^|service !SERVICE_NAME! start-type delayed-auto running-state
    exit /b 0
)
sc qc "!SERVICE_NAME!" >nul 2>&1
if errorlevel 1 (
    >"!BACKUP_FOLDER!\services\!SERVICE_NAME!.absent" echo absent
    if errorlevel 1 set "SERVICE_CAPTURE_FAILED=1"
    exit /b 0
)
set "SERVICE_START_TYPE="
for /f "tokens=3" %%T in ('sc qc "!SERVICE_NAME!" 2^>nul ^| findstr /c:"START_TYPE"') do set "SERVICE_START_TYPE=%%T"
if not defined SERVICE_START_TYPE (
    set "SERVICE_CAPTURE_FAILED=1"
    exit /b 0
)
set "SERVICE_RUNNING=0"
sc query "!SERVICE_NAME!" 2>nul | findstr /c:"RUNNING" >nul 2>&1
if not errorlevel 1 set "SERVICE_RUNNING=1"
set "SERVICE_DELAYED=0"
for /f "tokens=3" %%D in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\!SERVICE_NAME!" /v DelayedAutoStart 2^>nul ^| findstr /i "DelayedAutoStart"') do if /i "%%D"=="0x1" set "SERVICE_DELAYED=1"
>"!BACKUP_FOLDER!\services\!SERVICE_NAME!.state" echo start_type=!SERVICE_START_TYPE!
>>"!BACKUP_FOLDER!\services\!SERVICE_NAME!.state" echo delayed_auto=!SERVICE_DELAYED!
>>"!BACKUP_FOLDER!\services\!SERVICE_NAME!.state" echo running=!SERVICE_RUNNING!
if errorlevel 1 set "SERVICE_CAPTURE_FAILED=1"
exit /b 0

:backup_bcd
echo     Backing up boot configuration...
if "!PLAN_MODE!"=="1" (
    echo PLAN^|BACKUP^|bcdedit /export "!BACKUP_FOLDER!\bcd_backup"
    call :record_result "bcd" 0 "bcd_backup"
    exit /b 0
)
bcdedit /export "!BACKUP_FOLDER!\bcd_backup" >nul 2>&1
call :record_result "bcd" !ERRORLEVEL! "bcd_backup"
exit /b 0

:backup_power_scheme
echo     Backing up active power scheme...
if "!PLAN_MODE!"=="1" (
    echo PLAN^|QUERY^|powercfg /getactivescheme
    echo PLAN^|BACKUP^|powercfg /export "!BACKUP_FOLDER!\power_plan.pow" "{ACTIVE_POWER_GUID}"
    call :record_result "power_scheme" 0 "power_plan.pow"
    exit /b 0
)
set "ACTIVE_POWER_GUID="
for /f "tokens=4" %%G in ('powercfg /getactivescheme 2^>nul') do set "ACTIVE_POWER_GUID=%%G"
if not defined ACTIVE_POWER_GUID (
    call :record_result "power_scheme" 1 "power_plan.pow"
    exit /b 0
)
>"!BACKUP_FOLDER!\active_power_guid.txt" echo !ACTIVE_POWER_GUID!
if errorlevel 1 (
    call :record_result "power_scheme" 1 "active_power_guid.txt"
    exit /b 0
)
powercfg /export "!BACKUP_FOLDER!\power_plan.pow" "!ACTIVE_POWER_GUID!" >nul 2>&1
call :record_result "power_scheme" !ERRORLEVEL! "power_plan.pow"
exit /b 0

:backup_system_info
echo     Recording system information...
if "!PLAN_MODE!"=="1" (
    echo PLAN^|BACKUP^|systeminfo ^> "!BACKUP_FOLDER!\systeminfo.txt"
    call :record_result "system_info" 0 "systeminfo.txt"
    exit /b 0
)
systeminfo >"!BACKUP_FOLDER!\systeminfo.txt" 2>nul
call :record_result "system_info" !ERRORLEVEL! "systeminfo.txt"
exit /b 0

:record_result
set "RESULT_COMPONENT=%~1"
set "RESULT_CODE=%~2"
set "RESULT_ARTIFACT=%~3"
if "!RESULT_CODE!"=="0" (
    set /a BACKUP_SUCCESS+=1
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESULT^|!RESULT_COMPONENT!^|SUCCESS^|!RESULT_ARTIFACT!
    ) else (
        >>"!JOURNAL!" echo RESULT^|!RESULT_COMPONENT!^|SUCCESS^|!RESULT_ARTIFACT!
    )
) else (
    set /a BACKUP_FAILED+=1
    if "!PLAN_MODE!"=="1" (
        echo PLAN^|RESULT^|!RESULT_COMPONENT!^|FAILED^|!RESULT_ARTIFACT!^|exit=!RESULT_CODE!
    ) else (
        >>"!JOURNAL!" echo RESULT^|!RESULT_COMPONENT!^|FAILED^|!RESULT_ARTIFACT!^|exit=!RESULT_CODE!
    )
)
exit /b 0
