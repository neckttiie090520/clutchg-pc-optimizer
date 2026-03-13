@echo off
:: ============================================================================
:: ClutchG Optimizer - Telemetry & Privacy Blocker
:: ============================================================================
:: Purpose: Comprehensive telemetry, privacy, and tracking disabler
:: Source: Ghost-Optimizer (generalapply + telemetryapply), CS2-Ultimate-Optimization
:: Risk: MEDIUM — reversible registry changes, no security impact
:: Requires: Administrator privileges
:: ============================================================================

if "%~1"==":apply_all" goto :apply_all
if "%~1"==":apply_telemetry" goto :apply_telemetry
if "%~1"==":apply_privacy" goto :apply_privacy
if "%~1"==":apply_ads_suggestions" goto :apply_ads_suggestions
if "%~1"==":apply_xbox_dvr" goto :apply_xbox_dvr
if "%~1"==":reset_all" goto :reset_all
goto :eof

:apply_all
call :apply_telemetry
call :apply_privacy
call :apply_ads_suggestions
call :apply_xbox_dvr
call :log_telemetry "All telemetry & privacy tweaks applied"
goto :eof

:: ============================================================================
:: Core Telemetry
:: ============================================================================
:apply_telemetry
call :log_telemetry "Disabling Windows telemetry..."

:: Disable telemetry data collection
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v "AllowTelemetry" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v "MaxTelemetryAllowed" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Connected User Experiences
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "DisableEnterpriseAuthProxy" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable diagnostic data viewer
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack" /v "ShowedToastAtLevel" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable app diagnostics
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics" /v "Value" /t REG_SZ /d "Deny" /f >nul 2>&1

:: Stop and disable DiagTrack service
sc stop DiagTrack >nul 2>&1
sc config DiagTrack start= disabled >nul 2>&1

:: Stop and disable WAP Push service
sc stop dmwappushservice >nul 2>&1
sc config dmwappushservice start= disabled >nul 2>&1

:: Disable Diagnostics Hub
sc stop "diagnosticshub.standardcollector.service" >nul 2>&1
sc config "diagnosticshub.standardcollector.service" start= disabled >nul 2>&1

call :log_telemetry "Core telemetry disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Privacy Settings
:: ============================================================================
:apply_privacy
call :log_telemetry "Applying privacy tweaks..."

:: Disable advertising ID
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v "Enabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable activity history
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "PublishUserActivities" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "UploadUserActivities" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "EnableActivityFeed" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable feedback
reg add "HKCU\SOFTWARE\Microsoft\Siuf\Rules" /v "NumberOfSIUFInPeriod" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Siuf\Rules" /v "PeriodInNanoSeconds" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable tailored experiences
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy" /v "TailoredExperiencesWithDiagnosticDataEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Cortana
reg add "HKLM\SOFTWARE\Microsoft\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Bing search in Start Menu
reg add "HKCU\Software\Policies\Microsoft\Windows\Explorer" /v "DisableSearchBoxSuggestions" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v "BingSearchEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v "CortanaConsent" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v "SearchHistoryEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v "AllowSearchToUseLocation" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable web search indexing
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "ConnectedSearchUseWeb" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "ConnectedSearchUseWebOverMeteredConnections" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "DisableWebSearch" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable location tracking
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v "Value" /t REG_SZ /d "Deny" /f >nul 2>&1

:: Disable Geolocation Service
sc stop lfsvc >nul 2>&1
sc config lfsvc start= disabled >nul 2>&1

call :log_telemetry "Privacy tweaks applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Ads, Suggestions & Cloud Content
:: ============================================================================
:apply_ads_suggestions
call :log_telemetry "Disabling ads and suggestions..."

:: Disable Windows suggestions  
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SoftLandingEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "RotatingLockScreenEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "RotatingLockScreenOverlayEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable all SubscribedContent (start menu ads, suggestions, tips)
for %%s in (202914 280815 310093 314559 314563 338387 338388 338389 338393 353694 353696 353698) do (
    reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-%%sEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
)

:: Disable Windows Spotlight
reg add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableSpotlightCollectionOnDesktop" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableWindowsSpotlightFeatures" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableThirdPartySuggestions" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableWindowsConsumerFeatures" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableWindowsConsumerFeatures" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable News and Interests
reg add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v "AllowNewsAndInterests" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\PolicyManager\default\NewsAndInterests\AllowNewsAndInterests" /v "value" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Focus Assist notifications
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" /v "FocusAssist" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_telemetry "Ads and suggestions disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Xbox Game Bar & DVR
:: ============================================================================
:apply_xbox_dvr
call :log_telemetry "Disabling Xbox Game Bar and DVR..."

:: Disable Game DVR
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR" /v "value" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Game Bar overlay
reg add "HKCU\Software\Microsoft\GameBar" /v "UseNexusForGameBarEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\GameBar" /v "ShowStartupPanel" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Game Bar Presence Writer (reduces overhead)
reg add "HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter" /v "ActivationType" /t REG_DWORD /d 1 /f >nul 2>&1

:: Keep Game Mode enabled (it actually helps at the OS scheduler level)
reg add "HKCU\Software\Microsoft\GameBar" /v "AllowAutoGameMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f >nul 2>&1

call :log_telemetry "Xbox Game Bar & DVR disabled (Game Mode kept ON)"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Reset All
:: ============================================================================
:reset_all
call :log_telemetry "Resetting telemetry settings to defaults..."

:: Re-enable telemetry services
sc config DiagTrack start= auto >nul 2>&1
net start DiagTrack >nul 2>&1
sc config dmwappushservice start= auto >nul 2>&1

:: Re-enable telemetry collection
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v "AllowTelemetry" /f >nul 2>&1

:: Re-enable advertising
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v "Enabled" /t REG_DWORD /d 1 /f >nul 2>&1

:: Re-enable Game DVR
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 1 /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v "AllowGameDVR" /f >nul 2>&1

:: Re-enable Bing search
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Search" /v "BingSearchEnabled" /f >nul 2>&1

:: Re-enable location
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v "Value" /t REG_SZ /d "Allow" /f >nul 2>&1
sc config lfsvc start= auto >nul 2>&1

call :log_telemetry "Telemetry settings reset to defaults"
goto :eof

:: ============================================================================
:log_telemetry
if defined LOGFILE (
    echo [%TIME%] [Telemetry] %~1 >> "%LOGFILE%"
)
echo     [Telemetry] %~1
goto :eof
