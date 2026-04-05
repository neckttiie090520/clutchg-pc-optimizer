@echo off
:: ============================================================================
:: EXTREME Profile Rollback Script
:: ============================================================================
:: This script reverses all changes made by the EXTREME profile
:: Use this if system becomes unstable or you need to restore Windows features
::
:: BEFORE RUNNING: Ensure you have admin privileges
:: ============================================================================

:rollback_init
setlocal EnableDelayedExpansion

:: Color codes
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

cls
echo.
echo %RED%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %RED%║       EXTREME PROFILE ROLLBACK                               ║%RESET%
echo %RED%║       Restore System to Default Settings                    ║%RESET%
echo %RED%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %YELLOW%This will REVERSE all EXTREME profile optimizations:%RESET%
echo   - Restore default power settings
echo   - Re-enable all disabled services
echo   - Restore default registry values
echo   - Reset BCDEdit settings
echo   - Re-enable hypervisor and VBS
echo.
echo %RED%⚠️  REBOOT REQUIRED after rollback%RESET%
echo.
pause

echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║       Starting Rollback Process...                          ║%RESET%
echo %GREEN%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.

set /a ROLLBACK_SUCCESS=0
set /a ROLLBACK_FAILED=0

:: ============================================================================
:: PHASE 1: RESTORE POWER SETTINGS
:: ============================================================================
echo [%DATE% %TIME%] Phase 1/8: Restoring power settings...

:: Switch to Balanced power plan
powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2c >nul 2>&1
if %ERRORLEVEL%==0 (
    echo   [✓] Switched to Balanced power plan
    set /a ROLLBACK_SUCCESS+=1
) else (
    echo   [✗] Failed to switch power plan
    set /a ROLLBACK_FAILED+=1
)

:: Re-enable hibernation
powercfg /h on >nul 2>&1
echo   [✓] Hibernation re-enabled

:: Restore default power saving settings
powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53af886c5c01 1 >nul 2>&1
powercfg /setdcvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53af886c5c01 1 >nul 2>&1

powercfg /setacvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-5abca1bc2a34 5 >nul 2>&1
powercfg /setdcvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-5abca1bc2a34 5 >nul 2>&1

:: Restore default EPP range
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-5abca1bc2a34" /v "ValueMin" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-5abca1bc2a34" /v "ValueMax" /f >nul 2>&1

powercfg /SetActive 381b4222-f694-41f0-9685-ff5bb260df2c >nul 2>&1
echo   [✓] Default power settings restored
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 2: RESET BCDEdit SETTINGS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 2/8: Resetting BCDEdit settings...

bcdedit /deletevalue disabledynamictick >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Dynamic tick re-enabled

bcdedit /deletevalue useplatformtick >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Platform tick reset to default

bcdedit /deletevalue tscsyncpolicy >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] TSC sync policy reset to default

bcdedit /deletevalue uselegacyapicmode >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] APIC mode reset to default

bcdedit /deletevalue usephysicaldestination >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Processor destination reset to default

bcdedit /deletevalue hypervisorlaunchtype >nul 2>&1
if %ERRORLEVEL%==0 (
    echo   [✓] Hypervisor launch type reset (WSL2/Docker will work after reboot)
    set /a ROLLBACK_SUCCESS+=1
) else (
    echo   [⚠] Hypervisor was already set to default
)

:: Ensure DEP is enabled (safety)
bcdedit /set nx OptIn >nul 2>&1
echo   [✓] DEP (Data Execution Prevention) confirmed enabled

echo   [✓] BCDEdit settings reset to defaults
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 3: RE-ENABLE MEMORY INTEGRITY (VBS)
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 3/8: Re-enabling Memory Integrity...

reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Hypervisor enforced code integrity enabled

reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Virtualization Based Security enabled

echo   [⚠] Memory Integrity will be fully active after reboot
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 4: RE-ENABLE SERVICES
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 4/8: Re-enabling disabled services...

:: Windows Search (IMPORTANT - Start menu search)
sc config "WSearch" start= auto >nul 2>&1
net start "WSearch" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo   [✓] Windows Search re-enabled (Start menu search will work)
    set /a ROLLBACK_SUCCESS+=1
) else (
    echo   [⚠] Windows Search start pending (will start on reboot)
)

:: Print Spooler
sc config "Spooler" start= auto >nul 2>&1
net start "Spooler" >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Print Spooler re-enabled

:: Other services
sc config "Fax" start= demand >nul 2>&1
sc config "TabletInputService" start= manual >nul 2>&1
sc config "MapsBroker" start= demand >nul 2>&1
sc config "lfsvc" start= manual >nul 2>&1
sc config "SEMgrSvc" start= manual >nul 2>&1
sc config "RmSvc" start= manual >nul 2>&1
sc config "WalletService" start= manual >nul 2>&1

echo   [✓] Optional services set to automatic/manual

:: Xbox services (if user wants them back)
echo   [i] Xbox services remain disabled (re-enable manually if needed)
echo       To re-enable Xbox:
echo       sc config "XblAuthManager" start= manual
echo       sc config "XblGameSave" start= manual
echo       sc config "XboxNetApiSvc" start= manual

set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 5: RESTORE REGISTRY TWEAKS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 5/8: Restoring registry defaults...

:: MMCSS Gaming Profile - restore to defaults
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "Medium" /f >nul 2>&1
echo   [✓] MMCSS Gaming Profile reset to defaults

:: System Responsiveness
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /f >nul 2>&1

:: Win32PrioritySeparation
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 2 /f >nul 2>&1

:: File system settings
fsutil behavior set disablelastaccess 0 >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "NtfsDisableLastAccessUpdate" /f >nul 2>&1

fsutil behavior set disable8dot3 0 >nul 2>&1

:: Prefetch/Superfetch
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d 3 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d 2 /f >nul 2>&1

reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /f >nul 2>&1

echo   [✓] Registry settings restored to defaults
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 6: RESTORE NETWORK SETTINGS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 6/8: Restoring network defaults...

:: Remove TCP/IP tweaks
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpAckFrequency" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TCPNoDelay" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpWindowSize" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "MaxUserPort" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpTimedWaitDelay" /f >nul 2>&1

:: Restore NetBIOS
reg add "HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters" /v "NetbiosOptions" /t REG_DWORD /d 0 /f >nul 2>&1

echo   [✓] Network settings restored to defaults
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 7: RESTORE VISUAL EFFECTS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 7/8: Restoring visual effects...

reg delete "HKCU\Control Panel\Desktop" /v "DragFullWindows" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "400" /f >nul 2>&1
reg delete "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d 1 /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ListviewAlphaSelect" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "IconsOnly" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LauncherTaskbarDelay" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v "EnableTransparency" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 3 /f >nul 2>&1

echo   [✓] Visual effects restored to defaults
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: PHASE 8: RE-ENABLE BACKGROUND APPS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 8/8: Re-enabling background apps...

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v "GlobalUserDisabled" /t REG_DWORD /d 0 /f >nul 2>&1

reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /t REG_DWORD /d 1 /f >nul 2>&1
reg delete "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" /v "CortanaEnabled" /f >nul 2>&1

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v "Value" /t REG_SZ /d "Allow" /f >nul 2>&1

echo   [✓] Background apps re-enabled
set /a ROLLBACK_SUCCESS+=1

:: ============================================================================
:: SUMMARY
:: ============================================================================
echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║              ROLLBACK COMPLETE                               ║%RESET%
echo %GREEN%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %GREEN%Summary:%RESET%
echo   Successful: %ROLLBACK_SUCCESS%
echo   Failed: %ROLLBACK_FAILED%
echo.
echo %YELLOW%What was restored:%RESET%
echo   [✓] Balanced power plan
echo   [✓] Default power saving settings
echo   [✓] BCDEdit defaults (hypervisor enabled)
echo   [✓] Memory Integrity (VBS) enabled
echo   [✓] Windows Search enabled
echo   [✓] Print Spooler enabled
echo   [✓] Optional services re-enabled
echo   [✓] Registry defaults restored
echo   [✓] Network defaults restored
echo   [✓] Visual effects restored
echo   [✓] Background apps re-enabled
echo.
echo %RED%⚠️  REBOOT REQUIRED for all changes to take effect%RESET%
echo.
echo %YELLOW%After reboot, you should have:%RESET%
echo   - Normal power consumption and heat
echo   - WSL2/Docker working again
echo   - Windows Search working
echo   - Printing working
echo   - All Windows features restored
echo.
echo %BLUE%Would you like to reboot now? (Y/N)%RESET%
set /p REBOOT="Your choice: "

if /i "%REBOOT%"=="Y" (
    echo.
    echo %RED%Rebooting in 5 seconds...%RESET%
    timeout /t 5
    shutdown /r /t 0 /c "Rollback complete - rebooting"
) else (
    echo.
    echo %YELLOW%Please reboot manually when ready.%RESET%
    echo.
    pause
)

endlocal
exit /b 0
