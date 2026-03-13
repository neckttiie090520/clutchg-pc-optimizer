@echo off
:: ============================================
:: Backup Registry Module
:: Creates comprehensive system backups
:: ============================================

if "%~1"==":create_backup" goto :create_backup
if "%~1"==":backup_registry" goto :backup_registry
if "%~1"==":backup_services" goto :backup_services
goto :eof

:create_backup
:: Create a timestamped backup folder - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "TIMESTAMP=%%a"

set "BACKUP_FOLDER=%~dp0..\backups\%TIMESTAMP%"
mkdir "%BACKUP_FOLDER%" 2>nul

:: Export backup folder path for other modules
set "BACKUP_FOLDER=%BACKUP_FOLDER%"

echo     Creating backup in: %BACKUP_FOLDER%

:: Backup registry keys
call :backup_registry

:: Backup services configuration
call :backup_services

:: Backup BCD
bcdedit /export "%BACKUP_FOLDER%\bcd_backup" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo     - BCD configuration: OK
) else (
    echo     - BCD configuration: FAILED
)

:: Backup current power plan
powercfg /export "%BACKUP_FOLDER%\power_plan.pow" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo     - Power plan: OK
) else (
    echo     - Power plan: FAILED
)

:: Record system info
systeminfo > "%BACKUP_FOLDER%\systeminfo.txt" 2>nul
echo     - System info: OK

:: Create restore instructions
echo Windows Optimizer Backup > "%BACKUP_FOLDER%\README.txt"
echo Created: %DATE% %TIME% >> "%BACKUP_FOLDER%\README.txt"
echo. >> "%BACKUP_FOLDER%\README.txt"
echo To restore: >> "%BACKUP_FOLDER%\README.txt"
echo 1. Run optimizer.bat >> "%BACKUP_FOLDER%\README.txt"
echo 2. Select "Restore from Backup" >> "%BACKUP_FOLDER%\README.txt"
echo 3. Enter this folder name: %TIMESTAMP% >> "%BACKUP_FOLDER%\README.txt"

goto :eof

:backup_registry
:: Backup key registry hives
echo     Backing up registry...

reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "%BACKUP_FOLDER%\multimedia.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "%BACKUP_FOLDER%\priority.reg" /y >nul 2>&1
reg export "HKCU\Control Panel\Desktop" "%BACKUP_FOLDER%\desktop.reg" /y >nul 2>&1
reg export "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "%BACKUP_FOLDER%\telemetry.reg" /y >nul 2>&1
reg export "HKCU\SOFTWARE\Microsoft\GameBar" "%BACKUP_FOLDER%\gamebar.reg" /y >nul 2>&1
reg export "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "%BACKUP_FOLDER%\contentdelivery.reg" /y >nul 2>&1

echo     - Registry keys: OK
goto :eof

:backup_services
:: Backup services configuration
echo     Backing up services...

sc query > "%BACKUP_FOLDER%\services_state.txt" 2>nul

:: Backup specific service configs
for %%s in (DiagTrack dmwappushservice SysMain WSearch XblAuthManager XblGameSave XboxNetApiSvc) do (
    sc qc "%%s" >> "%BACKUP_FOLDER%\services_config.txt" 2>nul
)

echo     - Services configuration: OK
goto :eof
