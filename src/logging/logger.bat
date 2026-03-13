@echo off
:: ============================================
:: Logger Module
:: Handles all logging operations
:: ============================================

if "%~1"==":init_log" goto :init_log
if "%~1"==":log" goto :log
if "%~1"==":log_tweak" goto :log_tweak
if "%~1"==":close_log" goto :close_log
goto :eof

:init_log
:: Initialize log file with timestamp - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "LOG_TIMESTAMP=%%a"

set "LOGS_DIR=%~dp0..\logs"
mkdir "%LOGS_DIR%" 2>nul

set "LOGFILE=%LOGS_DIR%\optimizer_%LOG_TIMESTAMP%.log"

:: Write header
echo ================================================ > "%LOGFILE%"
echo Windows Optimizer Log                           >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"
echo Started: %DATE% %TIME%                          >> "%LOGFILE%"
echo Computer: %COMPUTERNAME%                        >> "%LOGFILE%"
echo User: %USERNAME%                                >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"
echo. >> "%LOGFILE%"

goto :eof

:log
:: General log message
:: Usage: call :log "Message"
if not defined LOGFILE exit /b 0
echo [%TIME%] %~1 >> "%LOGFILE%"
goto :eof

:log_tweak
:: Log tweak result
:: Usage: call :log_tweak "TweakName" "Result"
if not defined LOGFILE exit /b 0
echo [%TIME%] [TWEAK] %~1: %~2 >> "%LOGFILE%"
goto :eof

:close_log
:: Close log file with summary
if not defined LOGFILE exit /b 0

echo. >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"
echo Completed: %DATE% %TIME%                        >> "%LOGFILE%"
echo Tweaks Successful: %TWEAK_SUCCESS%              >> "%LOGFILE%"
echo Tweaks Failed: %TWEAK_FAILED%                   >> "%LOGFILE%"
echo Tweaks Skipped: %TWEAK_SKIPPED%                 >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"

goto :eof
