@echo off
:: ============================================================================
:: ClutchG Optimizer - Bloatware Remover
:: ============================================================================
:: Purpose: Safely remove pre-installed Windows bloatware apps
:: Source: Ghost-Optimizer (debloatapply)
:: Risk: HIGH — app removal is permanent (reinstallable from MS Store)
:: Requires: Administrator privileges
:: ============================================================================
:: SAFETY: Essential apps are whitelisted and NEVER removed
:: ============================================================================

if "%~1"==":apply_debloat" goto :apply_debloat
if "%~1"==":apply_onedrive" goto :apply_onedrive
if "%~1"==":apply_copilot" goto :apply_copilot
if "%~1"==":reset_info" goto :reset_info
goto :eof

:: ============================================================================
:: Remove Bloatware Apps
:: ============================================================================
:apply_debloat
call :log_debloat "Starting bloatware removal..."
call :log_debloat "Essential apps (Calculator, Photos, Store, Notepad, Terminal) are protected"

:: ─── Bing Apps ───
call :remove_app "Microsoft.BingNews"
call :remove_app "Microsoft.BingWeather"
call :remove_app "Microsoft.BingFinance"
call :remove_app "Microsoft.BingSports"
call :remove_app "Microsoft.BingTranslator"

:: ─── Social & Communication ───
call :remove_app "Microsoft.People"
call :remove_app "Microsoft.SkypeApp"
call :remove_app "Microsoft.MicrosoftTeams"
call :remove_app "Microsoft.YourPhone"

:: ─── Entertainment ───
call :remove_app "Microsoft.ZuneMusic"
call :remove_app "Microsoft.ZuneVideo"
call :remove_app "Microsoft.MicrosoftSolitaireCollection"
call :remove_app "Microsoft.GamingApp"
call :remove_app "SpotifyAB.SpotifyMusic"
call :remove_app "Disney.37853FC22B2CE"

:: ─── Productivity (rarely used) ───
call :remove_app "Microsoft.MicrosoftOfficeHub"
call :remove_app "Microsoft.Office.OneNote"
call :remove_app "Microsoft.MicrosoftStickyNotes"
call :remove_app "Microsoft.Getstarted"
call :remove_app "Microsoft.Todos"

:: ─── Maps & Location ───
call :remove_app "Microsoft.WindowsMaps"

:: ─── Mixed Reality / 3D ───
call :remove_app "Microsoft.MixedReality.Portal"
call :remove_app "Microsoft.Microsoft3DViewer"
call :remove_app "Microsoft.Print3D"
call :remove_app "Microsoft.3DBuilder"

:: ─── Other ───
call :remove_app "Microsoft.WindowsFeedbackHub"
call :remove_app "Microsoft.PowerAutomateDesktop"
call :remove_app "Clipchamp.Clipchamp"
call :remove_app "Microsoft.549981C3F5F10"
call :remove_app "MicrosoftCorporationII.QuickAssist"

:: ─── Third-party bloatware ───
call :remove_app "king.com.CandyCrushSaga"
call :remove_app "king.com.CandyCrushSodaSaga"
call :remove_app "king.com.BubbleWitch3Saga"
call :remove_app "FACEBOOK.FACEBOOK"
call :remove_app "Facebook.Instagram"
call :remove_app "BytedancePte.Ltd.TikTok"

call :log_debloat "Bloatware removal complete"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Disable OneDrive Auto-start
:: ============================================================================
:apply_onedrive
call :log_debloat "Disabling OneDrive auto-start..."

:: Remove OneDrive from startup
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OneDrive" /f >nul 2>&1

:: Prevent OneDrive from auto-installing
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f >nul 2>&1

:: Remove OneDrive from File Explorer sidebar
reg add "HKCR\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" /v "System.IsPinnedToNameSpaceTree" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCR\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" /v "System.IsPinnedToNameSpaceTree" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_debloat "OneDrive auto-start disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Disable Copilot / Recall (Windows 11)
:: ============================================================================
:apply_copilot
call :log_debloat "Disabling Copilot and Recall..."

:: Disable Windows Copilot
reg add "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" /v "TurnOffWindowsCopilot" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v "TurnOffWindowsCopilot" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable Windows Recall
reg add "HKCU\Software\Policies\Microsoft\Windows\WindowsAI" /v "DisableAIDataAnalysis" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v "DisableAIDataAnalysis" /t REG_DWORD /d 1 /f >nul 2>&1

:: Remove Copilot from taskbar
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ShowCopilotButton" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_debloat "Copilot and Recall disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: App Removal Helper
:: ============================================================================
:remove_app
set "APP_NAME=%~1"

:: Check if app is in the protected list
call :is_protected "%APP_NAME%"
if %ERRORLEVEL%==0 (
    call :log_debloat "PROTECTED: %APP_NAME% — skipping"
    goto :eof
)

:: Remove for current user
powershell -NoProfile -Command "Get-AppxPackage '%APP_NAME%' 2>$null | Remove-AppxPackage -ErrorAction SilentlyContinue" >nul 2>&1

:: Prevent reinstallation
powershell -NoProfile -Command "Get-AppxProvisionedPackage -Online 2>$null | Where-Object {$_.PackageName -like '*%APP_NAME%*'} | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue" >nul 2>&1

call :log_debloat "Removed: %APP_NAME%"
goto :eof

:: ============================================================================
:: Protected Apps (NEVER remove)
:: ============================================================================
:is_protected
set "CHECK_APP=%~1"

:: Essential apps list
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

:: ============================================================================
:: Reset Info
:: ============================================================================
:reset_info
call :log_debloat "To reinstall removed apps:"
call :log_debloat "  1. Open Microsoft Store"
call :log_debloat "  2. Search for the app name"
call :log_debloat "  3. Click Install"
call :log_debloat ""
call :log_debloat "Or run: Get-AppxPackage -AllUsers | Foreach {Add-AppxPackage -Register $_.InstallLocation\AppXManifest.xml}"
goto :eof

:: ============================================================================
:log_debloat
if defined LOGFILE (
    echo [%TIME%] [Debloat] %~1 >> "%LOGFILE%"
)
echo     [Debloat] %~1
goto :eof
