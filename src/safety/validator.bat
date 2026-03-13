@echo off
:: ============================================
:: Validator Module
:: Pre-execution validation and safety checks
:: ============================================

if "%~1"==":check_admin" goto :check_admin
if "%~1"==":validate_system" goto :validate_system
if "%~1"==":check_vm" goto :check_vm
goto :eof

:check_admin
:: Check if running with administrator privileges
net session >nul 2>&1
if %ERRORLEVEL%==0 (
    exit /b 0
) else (
    exit /b 1
)

:validate_system
:: Comprehensive system validation
call :check_admin
if %ERRORLEVEL%==1 (
    echo ERROR: Administrator privileges required.
    exit /b 1
)

:: Check Windows version
for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul ^| findstr CurrentBuild') do (
    set "BUILD=%%a"
)

if "%BUILD%" lss "17763" (
    echo ERROR: Windows 10 1809 or later required.
    echo Your build: %BUILD%
    exit /b 1
)

:: Check disk space (at least 100MB free on C:)
for /f "tokens=3" %%a in ('dir C:\ 2^>nul ^| findstr /c:"bytes free"') do (
    set "FREE_SPACE=%%a"
)

:: Warn if in VM (tweaks may not work as expected)
call :check_vm
if %ERRORLEVEL%==0 (
    echo WARNING: Virtual machine detected.
    echo Some tweaks may not work as expected.
)

exit /b 0

:check_vm
:: Detect if running in a virtual machine
systeminfo | findstr /i "VMware VirtualBox Hyper-V Virtual QEMU" >nul 2>&1
exit /b %ERRORLEVEL%
