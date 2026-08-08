@echo off
:: ============================================================================
:: ClutchG Optimizer - Bloatware Remover
:: ============================================================================
:: Purpose: Safely remove pre-installed Windows bloatware apps
:: Risk: HIGH - app removal is permanent (reinstallable from MS Store)
:: Requires: Administrator privileges
:: SAFETY: Essential apps are whitelisted and NEVER removed
:: ============================================================================

if "%~1"==":apply_debloat" goto :apply_debloat
if "%~1"==":apply_onedrive" goto :apply_onedrive
if "%~1"==":apply_copilot" goto :apply_copilot
if "%~1"==":reset_info" goto :reset_info
exit /b 0

:apply_debloat
set "MODULE_FAILURES=0"
call :log_debloat "Starting bloatware removal..."
call :log_debloat "Essential apps (Calculator, Photos, Store, Notepad, Terminal) are protected"

:: Bing Apps
call :remove_app "Microsoft.BingNews"
call :remove_app "Microsoft.BingWeather"
call :remove_app "Microsoft.BingFinance"
call :remove_app "Microsoft.BingSports"
call :remove_app "Microsoft.BingTranslator"

:: Social and Communication
call :remove_app "Microsoft.People"
call :remove_app "Microsoft.SkypeApp"
call :remove_app "Microsoft.MicrosoftTeams"
call :remove_app "Microsoft.YourPhone"

:: Entertainment
call :remove_app "Microsoft.ZuneMusic"
call :remove_app "Microsoft.ZuneVideo"
call :remove_app "Microsoft.MicrosoftSolitaireCollection"
call :remove_app "Microsoft.GamingApp"
call :remove_app "SpotifyAB.SpotifyMusic"
call :remove_app "Disney.37853FC22B2CE"

:: Productivity
call :remove_app "Microsoft.MicrosoftOfficeHub"
call :remove_app "Microsoft.Office.OneNote"
call :remove_app "Microsoft.MicrosoftStickyNotes"
call :remove_app "Microsoft.Getstarted"
call :remove_app "Microsoft.Todos"

:: Maps, Mixed Reality, and 3D
call :remove_app "Microsoft.WindowsMaps"
call :remove_app "Microsoft.MixedReality.Portal"
call :remove_app "Microsoft.Microsoft3DViewer"
call :remove_app "Microsoft.Print3D"
call :remove_app "Microsoft.3DBuilder"

:: Other
call :remove_app "Microsoft.WindowsFeedbackHub"
call :remove_app "Microsoft.PowerAutomateDesktop"
call :remove_app "Clipchamp.Clipchamp"
call :remove_app "Microsoft.549981C3F5F10"
call :remove_app "MicrosoftCorporationII.QuickAssist"

:: Third-party bloatware
call :remove_app "king.com.CandyCrushSaga"
call :remove_app "king.com.CandyCrushSodaSaga"
call :remove_app "king.com.BubbleWitch3Saga"
call :remove_app "FACEBOOK.FACEBOOK"
call :remove_app "Facebook.Instagram"
call :remove_app "BytedancePte.Ltd.TikTok"

if %MODULE_FAILURES% GTR 0 (
    call :log_debloat "Bloatware removal completed with failures"
    exit /b 1
)
call :log_debloat "Bloatware removal complete"
exit /b 0

:apply_onedrive
set "MODULE_FAILURES=0"
call :log_debloat "Disabling OneDrive auto-start..."
call :reg_delete_if_present "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" "OneDrive"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" "DisableFileSyncNGSC" "REG_DWORD" "1"
call :reg_add "HKCR\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" "System.IsPinnedToNameSpaceTree" "REG_DWORD" "0"
call :reg_add "HKCR\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" "System.IsPinnedToNameSpaceTree" "REG_DWORD" "0"
if %MODULE_FAILURES% GTR 0 (
    call :log_debloat "OneDrive changes completed with failures"
    exit /b 1
)
call :log_debloat "OneDrive auto-start disabled"
exit /b 0

:apply_copilot
set "MODULE_FAILURES=0"
call :log_debloat "Disabling Copilot and Recall..."
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" "TurnOffWindowsCopilot" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" "TurnOffWindowsCopilot" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Policies\Microsoft\Windows\WindowsAI" "DisableAIDataAnalysis" "REG_DWORD" "1"
call :reg_add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" "DisableAIDataAnalysis" "REG_DWORD" "1"
call :reg_add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "ShowCopilotButton" "REG_DWORD" "0"
if %MODULE_FAILURES% GTR 0 (
    call :log_debloat "Copilot and Recall changes completed with failures"
    exit /b 1
)
call :log_debloat "Copilot and Recall disabled"
exit /b 0

:remove_app
set "APP_NAME=%~1"
call :is_protected "%APP_NAME%"
if not errorlevel 1 (
    call :log_debloat "PROTECTED: %APP_NAME% - skipping"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)

set "APP_FOUND=0"
powershell -NoProfile -Command "$packages = @(Get-AppxPackage -Name '%APP_NAME%' -ErrorAction Stop); if ($packages.Count -eq 0) { exit 2 }; $packages | Remove-AppxPackage -ErrorAction Stop" >nul 2>&1
set "COMMAND_CODE=%ERRORLEVEL%"
if "%COMMAND_CODE%"=="0" (
    set "APP_FOUND=1"
) else if not "%COMMAND_CODE%"=="2" (
    call :log_debloat "FAILED current-user removal: %APP_NAME%"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)

powershell -NoProfile -Command "$packages = @(Get-AppxProvisionedPackage -Online -ErrorAction Stop | Where-Object {$_.PackageName -like '*%APP_NAME%*'}); if ($packages.Count -eq 0) { exit 2 }; $packages | Remove-AppxProvisionedPackage -Online -ErrorAction Stop | Out-Null" >nul 2>&1
set "COMMAND_CODE=%ERRORLEVEL%"
if "%COMMAND_CODE%"=="0" (
    set "APP_FOUND=1"
) else if not "%COMMAND_CODE%"=="2" (
    call :log_debloat "FAILED provisioned-package removal: %APP_NAME%"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)

if "%APP_FOUND%"=="0" (
    call :log_debloat "SKIPPED: %APP_NAME% is not installed"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)
call :log_debloat "Removed: %APP_NAME%"
set /a TWEAK_SUCCESS+=1
exit /b 0

:is_protected
set "CHECK_APP=%~1"
for %%p in (
    Microsoft.WindowsCalculator
    Microsoft.Windows.Photos
    Microsoft.WindowsStore
    Microsoft.WindowsNotepad
    Microsoft.WindowsTerminal
    Microsoft.DesktopAppInstaller
    Microsoft.WindowsCamera
    Microsoft.ScreenSketch
    Microsoft.Paint
    Microsoft.StorePurchaseApp
    Microsoft.SecHealthUI
    Microsoft.WindowsDefender
    Microsoft.WebMediaExtensions
    Microsoft.HEIFImageExtension
    Microsoft.VP9VideoExtensions
    Microsoft.WebpImageExtension
) do (
    if /i "%CHECK_APP%"=="%%p" exit /b 0
)
exit /b 1

:reg_add
reg add "%~1" /v "%~2" /t %~3 /d "%~4" /f >nul 2>&1
if errorlevel 1 (
    call :log_debloat "FAILED registry set: %~1\%~2"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:reg_delete_if_present
reg query "%~1" /v "%~2" >nul 2>&1
if errorlevel 1 (
    call :log_debloat "SKIPPED registry delete; value absent: %~1\%~2"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)
reg delete "%~1" /v "%~2" /f >nul 2>&1
if errorlevel 1 (
    call :log_debloat "FAILED registry delete: %~1\%~2"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:reset_info
call :log_debloat "To reinstall removed apps:"
call :log_debloat "  1. Open Microsoft Store"
call :log_debloat "  2. Search for the app name"
call :log_debloat "  3. Click Install"
call :log_debloat ""
call :log_debloat "Or run: Get-AppxPackage -AllUsers ^| Foreach {Add-AppxPackage -Register $_.InstallLocation\AppXManifest.xml}"
exit /b 0

:log_debloat
if defined LOGFILE (
    echo [%TIME%] [Debloat] %~1 >> "%LOGFILE%"
)
echo     [Debloat] %~1
exit /b 0
