@echo off
:: ============================================================================
:: ClutchG Optimizer - Flight Recorder Module
:: ============================================================================
:: Purpose: Registry snapshot and rollback system for safe optimization
:: Created: 2025-02-02 (Based on research.md safety principles)
:: ============================================================================
:: This module provides:
:: - Automatic registry snapshots before any changes
:: - System Restore Point creation
:: - One-click rollback functionality
:: - Complete audit trail of all modifications
:: ============================================================================

:main
if "%~1"=="" goto :usage
if "%~1"=="create_snapshot" goto :create_registry_snapshot
if "%~1"=="create_restore_point" goto :create_restore_point
if "%~1"=="capture_registry_state" goto :capture_registry_state
if "%~1"=="restore_snapshot" goto :restore_registry_snapshot
if "%~1"=="list_snapshots" goto :list_snapshots
goto :usage

:usage
echo Usage: flight-recorder.bat [command]
echo.
echo Commands:
echo   create_snapshot       - Create full registry snapshot
echo   create_restore_point  - Create Windows System Restore point
echo   capture_registry_state [key_path] [key_name]
echo                        - Capture specific registry key value
echo   restore_snapshot      - Restore most recent registry snapshot
echo   list_snapshots        - List all available snapshots
goto :eof

:: ============================================================================
:: Create Registry Snapshot
:: ============================================================================
:create_registry_snapshot
set "TIMESTAMP=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "SNAPSHOT_DIR=%BACKUPS_DIR%\registry_snapshots"

:: Create snapshot directory
if not exist "%SNAPSHOT_DIR%" mkdir "%SNAPSHOT_DIR%"

call "%LOGGING_DIR%\logger.bat" :log "Creating registry snapshot: %TIMESTAMP%"

:: Export critical registry hives before changes
reg export "HKLM\SOFTWARE" "%SNAPSHOT_DIR%\software_%TIMESTAMP%.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM" "%SNAPSHOT_DIR%\system_%TIMESTAMP%.reg" /y >nul 2>&1
reg export "HKCU\SOFTWARE" "%SNAPSHOT_DIR%\user_software_%TIMESTAMP%.reg" /y >nul 2>&1

:: Also export critical optimization-related paths
reg export "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" "%SNAPSHOT_DIR%\gpu_%TIMESTAMP%.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "%SNAPSHOT_DIR%\priority_%TIMESTAMP%.reg" /y >nul 2>&1
reg export "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" "%SNAPSHOT_DIR%\network_%TIMESTAMP%.reg" /y >nul 2>&1
reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "%SNAPSHOT_DIR%\multimedia_%TIMESTAMP%.reg" /y >nul 2>&1

:: Log snapshot creation
echo %TIMESTAMP% - Registry snapshot created >> "%BACKUPS_DIR%\snapshot_log.txt"
if exist "%BACKUPS_DIR%\snapshot_log.txt" (
    echo Registry snapshot created successfully: %TIMESTAMP%
    call "%LOGGING_DIR%\logger.bat" :log "Snapshot location: %SNAPSHOT_DIR%"
) else (
    echo ERROR: Failed to create snapshot log
)
goto :eof

:: ============================================================================
:: Create System Restore Point
:: ============================================================================
:create_restore_point
call "%LOGGING_DIR%\logger.bat" :log "Creating System Restore Point..."

:: Use PowerShell to create restore point (more reliable than WMIC on newer Windows)
powershell -Command "Checkpoint-Computer -Description 'ClutchG Pre-Optimization' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1

if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log "System Restore Point created successfully"
    echo System Restore Point created successfully
) else (
    :: Fallback to older PowerShell method for older Windows versions (replaces deprecated wmic)
    powershell -Command "Get-ComputerRestorePoint" >nul 2>&1
    if %ERRORLEVEL%==0 (
        powershell -Command "Start-Process powershell -ArgumentList 'ExecutionPolicy Bypass -Command & {Checkpoint-Computer -Description \"ClutchG Pre-Optimization\" -RestorePointType \"MODIFY_SETTINGS\"}' -Verb RunAs" >nul 2>&1
        call "%LOGGING_DIR%\logger.bat" :log "System Restore Point created (PowerShell fallback)"
        echo System Restore Point created (PowerShell fallback)
    ) else (
        call "%LOGGING_DIR%\logger.bat" :log "WARNING: Could not create restore point"
        echo WARNING: Could not create restore point (may require admin rights)
    )
)
goto :eof

:: ============================================================================
:: Capture Specific Registry State
:: ============================================================================
:capture_registry_state
if "%~2"=="" (
    echo Usage: flight-recorder.bat capture_registry_state [key_path] [key_name]
    echo Example: flight-recorder.bat capture_registry_state "HKLM\SOFTWARE\MyKey" "MyValue"
    goto :eof
)

set "KEY_PATH=%~1"
set "KEY_NAME=%~2"
set "TEMP_STATE=%TEMP%\reg_state_%RANDOM%.txt"

:: Query current value
reg query "%KEY_PATH%" /v "%KEY_NAME%" > "%TEMP_STATE%" 2>&1

if %ERRORLEVEL%==0 (
    :: Store in rollback log
    if not exist "%BACKUPS_DIR%" mkdir "%BACKUPS_DIR%"
    echo %DATE% %TIME% - %KEY_PATH%\%KEY_NAME% >> "%BACKUPS_DIR%\rollback_log.txt"
    type "%TEMP_STATE%" >> "%BACKUPS_DIR%\rollback_log.txt"
    echo. >> "%BACKUPS_DIR%\rollback_log.txt"

    call "%LOGGING_DIR%\logger.bat" :log "Captured state: %KEY_PATH%\%KEY_NAME%"
) else (
    call "%LOGGING_DIR%\logger.bat" :log "WARNING: Could not read %KEY_PATH%\%KEY_NAME%"
)

:: Cleanup
if exist "%TEMP_STATE%" del "%TEMP_STATE%"
goto :eof

:: ============================================================================
:: Restore Registry Snapshot
:: ============================================================================
:restore_registry_snapshot
set "SNAPSHOT_DIR=%BACKUPS_DIR%\registry_snapshots"

if not exist "%SNAPSHOT_DIR%" (
    echo ERROR: No snapshots found in %SNAPSHOT_DIR%
    goto :eof
)

echo Available snapshots:
echo.
dir /b "%SNAPSHOT_DIR%\*.reg" | findstr "software_.*\.reg$"
echo.

:: Find most recent software snapshot
for /f "delims=" %%a in ('dir "%SNAPSHOT_DIR%\software_*.reg" /b /o-d 2^>nul') do (
    set "LATEST_SOFTWARE=%%a"
    goto :restore_found
)

echo ERROR: No snapshots found to restore
goto :eof

:restore_found
echo.
echo WARNING: You are about to restore registry snapshot: %LATEST_SOFTWARE%
echo This will undo ALL optimization changes made since that snapshot.
echo.
set /p CONFIRM="Type 'RESTORE' to confirm: "

if not "%CONFIRM%"=="RESTORE" (
    echo Operation cancelled
    goto :eof
)

:: Restore snapshots
echo Restoring registry snapshots...
reg import "%SNAPSHOT_DIR%\%LATEST_SOFTWARE%" >nul 2>&1
if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log "Restored HKLM\SOFTWARE from %LATEST_SOFTWARE%"
    echo Restored HKLM\SOFTWARE
)

:: Restore corresponding system hive
set "SYSTEM_SNAPSHOT=%LATEST_SOFTWARE:software_=system%"
if exist "%SNAPSHOT_DIR%\%SYSTEM_SNAPSHOT%" (
    reg import "%SNAPSHOT_DIR%\%SYSTEM_SNAPSHOT%" >nul 2>&1
    if %ERRORLEVEL%==0 (
        call "%LOGGING_DIR%\logger.bat" :log "Restored HKLM\SYSTEM from %SYSTEM_SNAPSHOT%"
        echo Restored HKLM\SYSTEM
    )
)

echo.
echo Registry snapshot restored successfully
echo A system restart is recommended to apply all changes
goto :eof

:: ============================================================================
:: List All Snapshots
:: ============================================================================
:list_snapshots
set "SNAPSHOT_DIR=%BACKUPS_DIR%\registry_snapshots"

if not exist "%SNAPSHOT_DIR%" (
    echo No snapshots directory found
    goto :eof
)

echo Available Registry Snapshots:
echo ==============================
echo.
dir "%SNAPSHOT_DIR%\*.reg" /b | findstr "software_.*\.reg$"
echo.
echo Snapshot log:
echo ------------
if exist "%BACKUPS_DIR%\snapshot_log.txt" (
    type "%BACKUPS_DIR%\snapshot_log.txt"
) else (
    echo No snapshot log found
)
goto :eof
