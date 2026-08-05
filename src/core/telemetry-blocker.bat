@echo off
:: ============================================================================
:: ClutchG Optimizer - Telemetry & Privacy Blocker
:: ============================================================================
:: Purpose: Comprehensive telemetry, privacy, and tracking disabler
:: Risk: MEDIUM - reversible registry changes, no security impact
:: Requires: Administrator privileges
:: ============================================================================

if "%~1"==":apply_all" goto :apply_all
if "%~1"==":apply_telemetry" goto :apply_telemetry
if "%~1"==":apply_privacy" goto :apply_privacy
if "%~1"==":apply_ads_suggestions" goto :apply_ads_suggestions
if "%~1"==":apply_xbox_dvr" goto :apply_xbox_dvr
if "%~1"==":reset_all" goto :reset_all
exit /b 0

:apply_all
set "APPLY_ALL_FAILURES=0"
call :apply_telemetry
if errorlevel 1 set /a APPLY_ALL_FAILURES+=1
call :apply_privacy
if errorlevel 1 set /a APPLY_ALL_FAILURES+=1
call :apply_ads_suggestions
if errorlevel 1 set /a APPLY_ALL_FAILURES+=1
call :apply_xbox_dvr
if errorlevel 1 set /a APPLY_ALL_FAILURES+=1
if %APPLY_ALL_FAILURES% GTR 0 (
    call :log_telemetry "Telemetry and privacy application failed"
    exit /b 1
)
call :log_telemetry "All telemetry and privacy tweaks applied"
exit /b 0

:apply_telemetry
set "MODULE_FAILURES=0"
call :log_telemetry "Disabling Windows telemetry..."
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "AllowTelemetry" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" "AllowTelemetry" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" "MaxTelemetryAllowed" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "DisableEnterpriseAuthProxy" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack" "ShowedToastAtLevel" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics" "Value" "REG_SZ" "Deny"
call :disable_optional_service "DiagTrack"
call :disable_optional_service "dmwappushservice"
call :disable_optional_service "diagnosticshub.standardcollector.service"
if %MODULE_FAILURES% GTR 0 (
    call :log_telemetry "Core telemetry completed with failures"
    exit /b 1
)
call :log_telemetry "Core telemetry disabled"
exit /b 0

:apply_privacy
set "MODULE_FAILURES=0"
call :log_telemetry "Applying privacy tweaks..."
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" "Enabled" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "PublishUserActivities" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "UploadUserActivities" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "EnableActivityFeed" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Siuf\Rules" "NumberOfSIUFInPeriod" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Siuf\Rules" "PeriodInNanoSeconds" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy" "TailoredExperiencesWithDiagnosticDataEnabled" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows Search" "AllowCortana" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\Explorer" "DisableSearchBoxSuggestions" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" "BingSearchEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" "CortanaConsent" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" "SearchHistoryEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" "AllowSearchToUseLocation" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "ConnectedSearchUseWeb" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "ConnectedSearchUseWebOverMeteredConnections" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" "DisableWebSearch" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" "Value" "REG_SZ" "Deny"
call :disable_optional_service "lfsvc"
if %MODULE_FAILURES% GTR 0 (
    call :log_telemetry "Privacy tweaks completed with failures"
    exit /b 1
)
call :log_telemetry "Privacy tweaks applied"
exit /b 0

:apply_ads_suggestions
set "MODULE_FAILURES=0"
call :log_telemetry "Disabling ads and suggestions..."
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SystemPaneSuggestionsEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SoftLandingEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "RotatingLockScreenEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "RotatingLockScreenOverlayEnabled" "REG_DWORD" "0"
for %%s in (202914 280815 310093 314559 314563 338387 338388 338389 338393 353694 353696 353698) do call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SubscribedContent-%%sEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" "DisableSpotlightCollectionOnDesktop" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" "DisableWindowsSpotlightFeatures" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" "DisableThirdPartySuggestions" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" "DisableWindowsConsumerFeatures" "REG_DWORD" "1"
call :reg_add "HKLM\Software\Policies\Microsoft\Windows\CloudContent" "DisableWindowsConsumerFeatures" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" "AllowNewsAndInterests" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\PolicyManager\default\NewsAndInterests\AllowNewsAndInterests" "value" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" "FocusAssist" "REG_DWORD" "0"
if %MODULE_FAILURES% GTR 0 (
    call :log_telemetry "Ads and suggestions completed with failures"
    exit /b 1
)
call :log_telemetry "Ads and suggestions disabled"
exit /b 0

:apply_xbox_dvr
set "MODULE_FAILURES=0"
call :log_telemetry "Disabling Xbox Game Bar and DVR..."
call :reg_add "HKCU\System\GameConfigStore" "GameDVR_Enabled" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" "AllowGameDVR" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" "value" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\Software\Microsoft\GameBar" "UseNexusForGameBarEnabled" "REG_DWORD" "0"
call :reg_add "HKCU\SOFTWARE\Microsoft\GameBar" "ShowStartupPanel" "REG_DWORD" "0"
call :reg_add "HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter" "ActivationType" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Microsoft\GameBar" "AllowAutoGameMode" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Microsoft\GameBar" "AutoGameModeEnabled" "REG_DWORD" "1"
if %MODULE_FAILURES% GTR 0 (
    call :log_telemetry "Xbox Game Bar and DVR changes completed with failures"
    exit /b 1
)
call :log_telemetry "Xbox Game Bar and DVR disabled; Game Mode kept on"
exit /b 0

:reset_all
set "MODULE_FAILURES=0"
call :log_telemetry "Resetting telemetry settings to defaults..."
call :enable_optional_service "DiagTrack" "start"
call :enable_optional_service "dmwappushservice" "nostart"
call :reg_delete_if_present "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "AllowTelemetry"
call :reg_add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" "Enabled" "REG_DWORD" "1"
call :reg_add "HKCU\System\GameConfigStore" "GameDVR_Enabled" "REG_DWORD" "1"
call :reg_delete_if_present "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" "AllowGameDVR"
call :reg_delete_if_present "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" "BingSearchEnabled"
call :reg_add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" "Value" "REG_SZ" "Allow"
call :enable_optional_service "lfsvc" "nostart"
if %MODULE_FAILURES% GTR 0 (
    call :log_telemetry "Telemetry reset completed with failures"
    exit /b 1
)
call :log_telemetry "Telemetry settings reset to defaults"
exit /b 0

:reg_add
reg add "%~1" /v "%~2" /t %~3 /d "%~4" /f >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "FAILED registry set: %~1\%~2"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:reg_delete_if_present
reg query "%~1" /v "%~2" >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "SKIPPED registry delete; value absent: %~1\%~2"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)
reg delete "%~1" /v "%~2" /f >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "FAILED registry delete: %~1\%~2"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:disable_optional_service
sc query "%~1" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_telemetry "SKIPPED service; not installed: %~1"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_telemetry "FAILED to query service: %~1"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
sc query "%~1" | findstr /i /c:"STATE" | findstr /i /c:"RUNNING" >nul 2>&1
if not errorlevel 1 (
    sc stop "%~1" >nul 2>&1
    if errorlevel 1 (
        call :log_telemetry "FAILED to stop service: %~1"
        set /a MODULE_FAILURES+=1
        set /a TWEAK_FAILED+=1
        exit /b 1
    )
)
sc config "%~1" start= disabled >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "FAILED to disable service: %~1"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:enable_optional_service
sc query "%~1" >nul 2>&1
set "SERVICE_QUERY_CODE=%ERRORLEVEL%"
if not "%SERVICE_QUERY_CODE%"=="0" (
    if "%SERVICE_QUERY_CODE%"=="1060" (
        call :log_telemetry "SKIPPED service reset; not installed: %~1"
        set /a TWEAK_SKIPPED+=1
        exit /b 0
    )
    call :log_telemetry "FAILED to query service for reset: %~1"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
sc config "%~1" start= auto >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "FAILED to enable service: %~1"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
if /i not "%~2"=="start" (
    set /a TWEAK_SUCCESS+=1
    exit /b 0
)
net start "%~1" >nul 2>&1
if errorlevel 1 (
    call :log_telemetry "FAILED to start service: %~1"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:log_telemetry
if defined LOGFILE (
    echo [%TIME%] [Telemetry] %~1 >> "%LOGFILE%"
)
echo     [Telemetry] %~1
exit /b 0
