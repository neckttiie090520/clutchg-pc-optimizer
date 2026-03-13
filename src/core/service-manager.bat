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
goto :eof

:apply_service_tweaks
:: ============================================
:: Disable telemetry and non-essential services
:: NEVER disable security-related services
:: Enhanced: 2025-02-10 (Additional services from research)
:: ============================================

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
:: Check for touchscreen presence
powershell -Command "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*touch*' -or $_.FriendlyName -like '*pen*'}" >nul 2>&1
if %ERRORLEVEL%==1 (
    :: No touchscreen found, safe to disable
    call :safe_disable "TabletInputService" "Tablet Input Service"
) else (
    call :log_service "TabletInputService" "SKIPPED - Touchscreen detected"
)

:: Print Spooler - only if no printer configured
powershell -Command "Get-Printer | Select-Object -First 1" >nul 2>&1
if %ERRORLEVEL%==1 (
    :: No printer found, safe to disable
    call :safe_disable "Spooler" "Print Spooler"
) else (
    call :log_service "Spooler" "SKIPPED - Printer detected"
)

:: Set these to manual instead of disabled (may be needed occasionally)
:: Smart Manual Configuration (NEW from research)
call :set_manual "WSearch" "Windows Search"
call :set_manual "UsoSvc" "Windows Update Medic Service"
call :set_manual "DiagTrack" "Telemetry Service (Manual)"
call :set_manual "XblAuthManager" "Xbox Live Auth (Manual)"
call :set_manual "XblGameSave" "Xbox Game Save (Manual)"

:: SysMain (Superfetch) - Keep ENABLED on systems with sufficient RAM
:: RESEARCH: research.md shows disabling SysMain is a "long-standing myth"
:: EVIDENCE: No credible performance gains from disabling (debunked)
:: RECOMMENDATION: Keep enabled on systems with 8GB+ RAM
:: The line below sets it to manual (not disabled) for compatibility with existing code
call :set_manual "SysMain" "Superfetch/SysMain (Myth: disabling provides no benefit)"

goto :eof

:safe_disable
:: Safely disable a service with logging
set "SERVICE_NAME=%~1"
set "SERVICE_DESC=%~2"

:: Check if it's a critical service (should never happen, but safety first)
call :is_critical "%SERVICE_NAME%"
if %ERRORLEVEL%==0 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "BLOCKED - Critical service"
    set /a TWEAK_SKIPPED+=1
    goto :eof
)

:: Backup current state
sc qc "%SERVICE_NAME%" >> "%BACKUP_FOLDER%\services_backup.txt" 2>nul

:: Stop and disable
sc stop "%SERVICE_NAME%" >nul 2>&1
sc config "%SERVICE_NAME%" start= disabled >nul 2>&1

if %ERRORLEVEL%==0 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "Disabled"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED or not found"
    set /a TWEAK_SKIPPED+=1
)
goto :eof

:set_manual
:: Set service to manual start (safer than disabled)
set "SERVICE_NAME=%~1"
set "SERVICE_DESC=%~2"

sc qc "%SERVICE_NAME%" >> "%BACKUP_FOLDER%\services_backup.txt" 2>nul
sc config "%SERVICE_NAME%" start= demand >nul 2>&1

if %ERRORLEVEL%==0 (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "Set to Manual"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_service "%SERVICE_DESC% (%SERVICE_NAME%)" "FAILED"
    set /a TWEAK_FAILED+=1
)
goto :eof

:is_critical
:: Check if service is on the critical/protected list
:: Returns 0 if critical (do not disable), 1 if safe to disable
set "CHECK_SERVICE=%~1"

:: List of services that should NEVER be disabled
:: Based on research.md: Critical system services that break Windows if disabled
:: 17/28 repos analyzed disable WinDefend (F grade) - we NEVER do this
for %%c in (
    WinDefend
    SecurityHealthService
    wuauserv
    CryptSvc
    RpcSs
    EventLog
    TrustedInstaller
    BITS
    wscsvc
    Winmgmt
    PlugPlay
    DcomLaunch
    LSM
    Schedule
    Power
    Netman
    MpsSvc
    BFE
    Dnscache
    NlaSvc
    Sppsvc
    SamSs
    AppIDSvc
    AppReadiness
) do (
    if /i "%CHECK_SERVICE%"=="%%c" exit /b 0
)
exit /b 1

:reset_all
echo     Resetting services to automatic start...

:: Re-enable telemetry services
for %%s in (DiagTrack dmwappushservice diagnosticshub.standardcollector.service) do (
    sc config "%%s" start= auto >nul 2>&1
)

:: Re-enable Xbox services
for %%s in (XblAuthManager XblGameSave XboxNetApiSvc XboxGipSvc) do (
    sc config "%%s" start= auto >nul 2>&1
)

:: Re-enable other services
for %%s in (RetailDemo MapsBroker lfsvc SharedAccess WSearch SysMain) do (
    sc config "%%s" start= auto >nul 2>&1
)

:: Re-enable additional services (NEW)
for %%s in (Fax WFDSConMgrSvc TabletInputService Spooler UsoSvc) do (
    sc config "%%s" start= auto >nul 2>&1
)

call :log_service "All services reset" "SUCCESS"
goto :eof

:disable_service
:: Manual disable command
:: Usage: call :disable_service "ServiceName"
call :safe_disable "%~1" "%~1"
goto :eof

:enable_service
:: Re-enable a service
sc config "%~1" start= auto >nul 2>&1
net start "%~1" >nul 2>&1
call :log_service "%~1" "Enabled"
goto :eof

:log_service
if defined LOGFILE (
    echo [%TIME%] [Service] %~1: %~2 >> "%LOGFILE%"
)
echo     [Service] %~1: %~2
goto :eof
