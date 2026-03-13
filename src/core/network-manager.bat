@echo off
:: ============================================
:: Network Manager Module
:: Handles network optimization
:: ============================================

if "%~1"==":apply_network_tweaks" goto :apply_network_tweaks
if "%~1"==":set_dns" goto :set_dns
if "%~1"==":reset_all" goto :reset_all
goto :eof

:apply_network_tweaks
:: ============================================
:: Network optimizations
:: Note: Many "network tweaks" are placebo.
:: We only apply tweaks with documented benefit.
:: ============================================

:: Flush DNS cache
ipconfig /flushdns >nul 2>&1
call :log_network "DNS cache flushed" "SUCCESS"

:: Reset Winsock (if needed)
:: Note: Only uncomment if experiencing network issues
:: netsh winsock reset >nul 2>&1

:: Disable LMHOSTS lookup
call :reg_network "HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters" "EnableLMHOSTS" "REG_DWORD" "0"

:: Disable NetBIOS over TCP/IP (enhances security)
:: Note: May break some legacy network features
:: Uncomment only if not using legacy network shares
:: call :reg_network "HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters\Interfaces" "NetbiosOptions" "REG_DWORD" "2"

:: Network Throttling Index
:: Note: This is often cited but has minimal real-world impact
:: The default value is already optimized for most scenarios
:: call :reg_network "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "NetworkThrottlingIndex" "REG_DWORD" "4294967295"

:: Disable Nagle's algorithm for specific applications
:: Note: This should be done per-application, not globally
:: Global changes can increase network overhead

set /a TWEAK_SUCCESS+=1
goto :eof

:set_dns
:: Set DNS servers
:: Usage: call :set_dns "AdapterName" "Primary" "Secondary"
set "ADAPTER=%~1"
set "DNS1=%~2"
set "DNS2=%~3"

if "%DNS1%"=="" set "DNS1=1.1.1.1"
if "%DNS2%"=="" set "DNS2=8.8.8.8"

netsh interface ipv4 set dns name="%ADAPTER%" static %DNS1% primary >nul 2>&1
netsh interface ipv4 add dns name="%ADAPTER%" %DNS2% index=2 >nul 2>&1

call :log_network "DNS set to %DNS1%, %DNS2% on %ADAPTER%" "SUCCESS"
goto :eof

:reset_all
:: Reset network settings to defaults
echo     Resetting network settings...

:: Reset DND to automatic
for /f "tokens=*" %%a in ('netsh interface show interface ^| findstr /i "Connected"') do (
    for /f "tokens=4" %%b in ("%%a") do (
        netsh interface ipv4 set dns name="%%b" dhcp >nul 2>&1
    )
)

:: Re-enable LMHOSTS
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters" /v "EnableLMHOSTS" /f >nul 2>&1

:: Flush DNS
ipconfig /flushdns >nul 2>&1

call :log_network "Network settings reset" "SUCCESS"
goto :eof

:reg_network
:: Set network registry value
set "REG_KEY=%~1"
set "REG_VALUE=%~2"
set "REG_TYPE=%~3"
set "REG_DATA=%~4"

reg add "%REG_KEY%" /v "%REG_VALUE%" /t %REG_TYPE% /d "%REG_DATA%" /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_network "%REG_VALUE%=%REG_DATA%" "SUCCESS"
) else (
    call :log_network "%REG_VALUE%=%REG_DATA%" "FAILED"
)
goto :eof

:log_network
if defined LOGFILE (
    echo [%TIME%] [Network] %~1: %~2 >> "%LOGFILE%"
)
echo     [Network] %~1: %~2
goto :eof
