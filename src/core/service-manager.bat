@echo off
:: ============================================
:: Service Manager Module (Enhanced)
:: Handles Windows service optimization with safety whitelist
:: Enhanced: 2025-02-02 (Based on research.md safety principles)
:: ============================================
:: SAFETY: Uses whitelist-based approach to protect critical services
:: RESEARCH: 60.7% of optimization tools disable services unsafely
:: ============================================

if "%~1"==":apply_service_tweaks" goto :apply_service_tweaks
if "%~1"==":reset_all" goto :reset_all
if "%~1"==":disable_service" goto :disable_service
if "%~1"==":enable_service" goto :enable_service
exit /b 0

:apply_service_tweaks
:: ============================================
:: Disable telemetry and non-essential services
:: NEVER disable security-related services
:: Enhanced: 2025-02-10 (Additional services from research)
:: ============================================
set "MODULE_FAILURES=0"

:: Telemetry services (safe to disable)
call :safe_disable "DiagTrack" "Connected User Experiences and Telemetry"
call :safe_disable "dmwappushservice" "WAP Push Message Routing Service"
call :safe_disable "diagnosticshub.standardcollector.service" "Diagnostics Hub"

:: Xbox services (if not using Xbox features)
call :safe_disable "XblAuthManager" "Xbox Live Auth Manager"
call :safe_disable "XblGameSave" "Xbox Live Game Save"
call :safe_disable "XboxNetApiSvc" "Xbox Live Networking Service"
call :safe_disable "XboxGipSvc" "Xbox Accessory Management Service"

:: Other non-essential services
call :safe_disable "RetailDemo" "Retail Demo Service"
call :safe_disable "MapsBroker" "Downloaded Maps Manager"
call :safe_disable "lfsvc" "Geolocation Service"
call :safe_disable "SharedAccess" "Internet Connection Sharing"

:: Additional safe services (NEW from research)
call :safe_disable "Fax" "Fax Service"
call :safe_disable "WFDSConMgrSvc" "Windows Phone Discovery Service"

:: Tablet Input Service - only if no touchscreen/tablet
powershell -NoProfile -Command "try { $device = Get-PnpDevice -ErrorAction Stop | Where-Object {$_.FriendlyName -like '*touch*' -or $_.FriendlyName -like '*pen*'} | Select-Object -First 1; if ($device) { exit 0 } else { exit 1 } } catch { exit 2 }" >nul 2>&1
if errorlevel 2 (
    call :log_service "TabletInputService" "FAILED - Could not detect touchscreen hardware"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
) else if errorlevel 1 (
    call :safe_disable "TabletInputService" "Tablet Input Service"
) else (
    call :log_service "TabletInputService" "SKIPPED - Touchscreen detected"
    set /a TWEAK_SKIPPED+=1
)

:: Print Spooler - only if no printer configured
powershell -NoProfile -Command "try { $printer = Get-Printer -ErrorAction Stop | Select-Object -First 1; if ($printer) { exit 0 } else { exit 1 } } catch { exit 2 }" >nul 2>&1
if errorlevel 2 (
    call :log_service "Spooler" "FAILED - Could not detect configured printers"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
) else if errorlevel 1 (
    call :safe_disable "Spooler" "Print Spooler"
) else (
    call :log_service "Spooler" "SKIPPED - Printer detected"
    set /a TWEAK_SKIPPED+=1
)

:: Set these to manual instead of disabled (may be needed occasionally)
call :set_manual "WSearch" "Windows Search"
call :set_manual "UsoSvc" "Windows Update Medic Service"
call :set_manual "DiagTrack" "Telemetry Service (Manual)"
call :set_manual "XblAuthManager" "Xbox Live Auth (Manual)"
call :set_manual "XblGameSave" "Xbox Game Save (Manual)"

:: SysMain (Superfetch) - Keep ENABLED on systems with sufficient RAM
:: RESEARCH: research.md shows disabling SysMain is a "long-standing myth"
call :set_manual "SysMain" "Superfetch/SysMain (Myth: disabling provides no benefit)"

if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:safe_disable
:: Safely disable a service with logging. Missing services are explicit skips.
set "SERVICE_NAME=%~1"
set "SERVICE_DESC=%~2"
set "OPERATION_FAILED=0"

call :is_critical "%SERVICE_NAME%"
if not errorlevel 1 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "BLOCKED - Critical service"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)

sc query "%SERVICE_NAME%" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "SKIPPED - Service not installed"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not query service"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)

if defined BACKUP_FOLDER (
    sc qc "%SERVICE_NAME%" >> "%BACKUP_FOLDER%\services_backup.txt" 2>nul
    if errorlevel 1 (
        call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not back up service state"
        set /a MODULE_FAILURES+=1
        set /a TWEAK_FAILED+=1
        exit /b 1
    )
)

sc query "%SERVICE_NAME%" | findstr /i /c:"RUNNING" >nul 2>&1
if not errorlevel 1 (
    sc stop "%SERVICE_NAME%" >nul 2>&1
    if errorlevel 1 (
        call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not stop service"
        set /a MODULE_FAILURES+=1
        set "OPERATION_FAILED=1"
    )
)

sc config "%SERVICE_NAME%" start= disabled >nul 2>&1
if errorlevel 1 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not disable service"
    set /a MODULE_FAILURES+=1
    set "OPERATION_FAILED=1"
)

if "%OPERATION_FAILED%"=="1" (
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "Disabled"
set /a TWEAK_SUCCESS+=1
exit /b 0

:set_manual
:: Set service to manual start (safer than disabled). Missing services are skips.
set "SERVICE_NAME=%~1"
set "SERVICE_DESC=%~2"

sc query "%SERVICE_NAME%" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "SKIPPED - Service not installed"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not query service"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)

if defined BACKUP_FOLDER (
    sc qc "%SERVICE_NAME%" >> "%BACKUP_FOLDER%\services_backup.txt" 2>nul
    if errorlevel 1 (
        call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not back up service state"
        set /a MODULE_FAILURES+=1
        set /a TWEAK_FAILED+=1
        exit /b 1
    )
)

sc config "%SERVICE_NAME%" start= demand >nul 2>&1
if errorlevel 1 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED - Could not set Manual"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "Set to Manual"
set /a TWEAK_SUCCESS+=1
exit /b 0

:is_critical
:: Returns 0 if critical (do not disable), 1 if safe to disable.
set "CHECK_SERVICE=%~1"
for %%c in (
    WinDefend SecurityHealthService wuauserv CryptSvc RpcSs EventLog
    TrustedInstaller BITS wscsvc Winmgmt PlugPlay DcomLaunch LSM Schedule
    Power Netman MpsSvc BFE Dnscache NlaSvc Sppsvc SamSs AppIDSvc AppReadiness
) do (
    if /i "%CHECK_SERVICE%"=="%%c" exit /b 0
)
exit /b 1

:reset_all
set "MODULE_FAILURES=0"
echo     Resetting services to automatic start...
for %%s in (
    DiagTrack dmwappushservice diagnosticshub.standardcollector.service
    XblAuthManager XblGameSave XboxNetApiSvc XboxGipSvc
    RetailDemo MapsBroker lfsvc SharedAccess WSearch SysMain
    Fax WFDSConMgrSvc TabletInputService Spooler UsoSvc
) do call :reset_service "%%s"

if %MODULE_FAILURES% GTR 0 (
    call :log_service "Service reset" "FAILED - One or more required commands failed"
    exit /b 1
)
call :log_service "All services reset" "SUCCESS"
exit /b 0

:reset_service
set "SERVICE_NAME=%~1"
sc query "%SERVICE_NAME%" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_service "%SERVICE_NAME%" "SKIPPED - Service not installed"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_service "%SERVICE_NAME%" "FAILED - Could not query service"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
sc config "%SERVICE_NAME%" start= auto >nul 2>&1
if errorlevel 1 (
    call :log_service "%SERVICE_NAME%" "FAILED - Could not set Automatic"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
exit /b 0

:disable_service
set "MODULE_FAILURES=0"
call :safe_disable "%~1" "%~1"
if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:enable_service
set "MODULE_FAILURES=0"
set "SERVICE_NAME=%~1"
sc query "%SERVICE_NAME%" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_service "%SERVICE_NAME%" "SKIPPED - Service not installed"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_service "%SERVICE_NAME%" "FAILED - Could not query service"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
sc config "%SERVICE_NAME%" start= auto >nul 2>&1
if errorlevel 1 (
    call :log_service "%SERVICE_NAME%" "FAILED - Could not set Automatic"
    set /a MODULE_FAILURES+=1
)
sc query "%SERVICE_NAME%" | findstr /i /c:"RUNNING" >nul 2>&1
if errorlevel 1 (
    net start "%SERVICE_NAME%" >nul 2>&1
    if errorlevel 1 (
        call :log_service "%SERVICE_NAME%" "FAILED - Could not start service"
        set /a MODULE_FAILURES+=1
    )
)
if %MODULE_FAILURES% GTR 0 (
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_service "%SERVICE_NAME%" "Enabled"
set /a TWEAK_SUCCESS+=1
exit /b 0

:log_service
if defined LOGFILE (
    echo [%TIME%] [Service] %~1: %~2 >> "%LOGFILE%"
)
echo     [Service] %~1: %~2
exit /b 0
