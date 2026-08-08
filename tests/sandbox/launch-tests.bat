@echo off
:: ============================================================================
:: ClutchG V&V — Host Launcher
:: ============================================================================
:: Runs on the HOST machine. Materializes a portable Windows Sandbox template,
:: launches it, waits for results, then displays a summary.
::
:: Usage: launch-tests.bat [config]
::   config: default | nogpu | nonet
::
:: Prerequisites:
::   - Windows Sandbox feature must be enabled
:: ============================================================================

setlocal DisableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "RESULTS_DIR=%REPO_ROOT%\tests\sandbox\results"
set "CONFIG=%~1"

if "%CONFIG%"=="" set "CONFIG=default"

:: Select the portable template.
if "%CONFIG%"=="default" set "WSB_TEMPLATE=%SCRIPT_DIR%clutchg-test.wsb"
if "%CONFIG%"=="nogpu"   set "WSB_TEMPLATE=%SCRIPT_DIR%clutchg-test-nogpu.wsb"
if "%CONFIG%"=="nonet"   set "WSB_TEMPLATE=%SCRIPT_DIR%clutchg-test-nonet.wsb"

if not defined WSB_TEMPLATE (
    echo ERROR: Unknown config "%CONFIG%". Use: default, nogpu, nonet
    exit /b 1
)

if not exist "%WSB_TEMPLATE%" (
    echo ERROR: WSB template not found: %WSB_TEMPLATE%
    exit /b 1
)

:: Check if Windows Sandbox is available.
where WindowsSandbox.exe >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Windows Sandbox is not installed or not enabled.
    echo.
    echo To enable, run in an admin PowerShell:
    echo   Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
    echo Then restart your PC.
    exit /b 1
)

mkdir "%RESULTS_DIR%" 2>nul

:: Materialize host paths into a temporary config. Values are passed through the
:: environment so shell metacharacters stay out of the PowerShell command, then
:: XML-escaped before replacement.
set "WSB_SRC=%REPO_ROOT%\src"
set "WSB_HARNESS=%REPO_ROOT%\tests\sandbox"
set "WSB_RESULTS=%RESULTS_DIR%"
set "WSB_FILE=%TEMP%\clutchg-sandbox-%RANDOM%-%RANDOM%.wsb"

powershell.exe -NoProfile -NonInteractive -Command "$template = [IO.File]::ReadAllText($env:WSB_TEMPLATE); $template = $template.Replace('__CLUTCHG_SRC__', [Security.SecurityElement]::Escape($env:WSB_SRC)); $template = $template.Replace('__CLUTCHG_HARNESS__', [Security.SecurityElement]::Escape($env:WSB_HARNESS)); $template = $template.Replace('__CLUTCHG_RESULTS__', [Security.SecurityElement]::Escape($env:WSB_RESULTS)); $utf8 = New-Object System.Text.UTF8Encoding($false); [IO.File]::WriteAllText($env:WSB_FILE, $template, $utf8)"
if errorlevel 1 (
    echo ERROR: Could not materialize Windows Sandbox configuration.
    if exist "%WSB_FILE%" del /q "%WSB_FILE%" >nul 2>&1
    exit /b 1
)

:: Count existing result files to detect a new run.
set /a BEFORE_COUNT=0
for %%f in ("%RESULTS_DIR%\vv-summary_*.txt") do set /a BEFORE_COUNT+=1

echo.
echo  ================================================================
echo   ClutchG V^&V Test Launcher
echo   Config: %CONFIG%
echo   Template: %WSB_TEMPLATE%
echo  ================================================================
echo.
echo  Launching Windows Sandbox...
echo  The sandbox will auto-run all tests and write results to:
echo    %RESULTS_DIR%
echo.
echo  Please wait for the sandbox to finish (it will show results
echo  inside the sandbox window, then prompt to close).
echo.

:: Launch the generated concrete sandbox configuration.
start "" "%WSB_FILE%"
if errorlevel 1 (
    echo ERROR: Windows Sandbox could not be launched.
    del /q "%WSB_FILE%" >nul 2>&1
    exit /b 1
)

:: Wait for results.
echo  Waiting for test results...
echo  (Checking every 10 seconds for new result files)
echo.

:wait_loop
timeout /t 10 /nobreak >nul

set /a AFTER_COUNT=0
for %%f in ("%RESULTS_DIR%\vv-summary_*.txt") do set /a AFTER_COUNT+=1

if %AFTER_COUNT% gtr %BEFORE_COUNT% (
    echo  New results detected!
    goto :show_results
)

:: Check if sandbox process is still running.
tasklist /fi "imagename eq WindowsSandbox.exe" 2>nul | findstr /i "WindowsSandbox" >nul
if %ERRORLEVEL% neq 0 goto :sandbox_closed

goto :wait_loop

:sandbox_closed
:: Check once more in case the result arrived as Sandbox exited.
set /a AFTER_COUNT=0
for %%f in ("%RESULTS_DIR%\vv-summary_*.txt") do set /a AFTER_COUNT+=1
if %AFTER_COUNT% gtr %BEFORE_COUNT% goto :show_results

echo  Sandbox closed without producing results.
echo  This may happen if the sandbox couldn't write to the results folder.
del /q "%WSB_FILE%" >nul 2>&1
exit /b 1

:show_results
echo.
echo  ================================================================
echo   TEST RESULTS
echo  ================================================================

:: Find the newest summary file.
set "NEWEST="
for %%f in ("%RESULTS_DIR%\vv-summary_*.txt") do set "NEWEST=%%f"

if defined NEWEST (
    for /f "usebackq tokens=1-5 delims=," %%a in ("%NEWEST%") do (
        echo   Total:   %%a
        echo   Passed:  %%b
        echo   Failed:  %%c
        echo   Skipped: %%d
        echo   Warned:  %%e
    )
) else (
    echo   Could not parse summary.
)

:: Find the newest full result file.
set "NEWEST_FULL="
for %%f in ("%RESULTS_DIR%\vv-results_*.txt") do set "NEWEST_FULL=%%f"

echo  ================================================================
echo.
if defined NEWEST_FULL echo  Full results: %NEWEST_FULL%

:: Find JSON.
set "NEWEST_JSON="
for %%f in ("%RESULTS_DIR%\vv-results_*.json") do set "NEWEST_JSON=%%f"
if defined NEWEST_JSON echo  JSON results: %NEWEST_JSON%

del /q "%WSB_FILE%" >nul 2>&1
echo.
endlocal
exit /b 0
