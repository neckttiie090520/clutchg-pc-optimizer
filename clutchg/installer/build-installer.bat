@echo off
:: ============================================================
:: ClutchG — Build Installer
:: ============================================================
:: Prerequisites:
::   1. PyInstaller build is complete:
::        cd clutchg && python build.py
::      Output: clutchg\dist\ClutchG\ClutchG.exe
::
::   2. Inno Setup 6 is installed.
::      Default path: C:\Program Files (x86)\Inno Setup 6\ISCC.exe
::      Set ISCC env var to override.
::
:: Usage (from repo root or clutchg\):
::   installer\build-installer.bat
::
:: Output:
::   clutchg\installer\output\ClutchG-Setup-1.0.0.exe
:: ============================================================

setlocal EnableDelayedExpansion

:: ── Locate this script's directory (clutchg\installer\) ──
set "SCRIPT_DIR=%~dp0"
set "INSTALLER_DIR=%SCRIPT_DIR%"
set "CLUTCHG_DIR=%SCRIPT_DIR%.."
set "DIST_DIR=%CLUTCHG_DIR%\dist\ClutchG"
set "ISS_FILE=%INSTALLER_DIR%ClutchG.iss"

:: ── Locate ISCC.exe ───────────────────────────────────────
if "%ISCC%"=="" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

echo ============================================================
echo  ClutchG Installer Builder
echo ============================================================
echo.

:: ── Check Inno Setup is installed ────────────────────────
if not exist "%ISCC%" (
    echo ERROR: Inno Setup 6 not found at:
    echo   %ISCC%
    echo.
    echo Please install Inno Setup 6 from:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Or set the ISCC environment variable to the full path of ISCC.exe:
    echo   set ISCC=C:\path\to\Inno Setup 6\ISCC.exe
    echo.
    exit /b 1
)

:: ── Check that the PyInstaller build exists ───────────────
if not exist "%DIST_DIR%\ClutchG.exe" (
    echo ERROR: PyInstaller build not found at:
    echo   %DIST_DIR%\ClutchG.exe
    echo.
    echo Run the build first:
    echo   cd clutchg
    echo   python build.py
    echo.
    exit /b 1
)

:: ── Create output dir ────────────────────────────────────
if not exist "%INSTALLER_DIR%output" (
    mkdir "%INSTALLER_DIR%output"
)

:: ── Run ISCC ─────────────────────────────────────────────
echo Inno Setup : %ISCC%
echo Script     : %ISS_FILE%
echo Output dir : %INSTALLER_DIR%output
echo.
echo Building installer...
echo.

"%ISCC%" "%ISS_FILE%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================================
    echo  BUILD FAILED  (ISCC exit code: %ERRORLEVEL%)
    echo ============================================================
    exit /b %ERRORLEVEL%
)

:: ── Success ───────────────────────────────────────────────
echo.
echo ============================================================
echo  BUILD SUCCESSFUL
echo ============================================================
echo.

:: Show output file size
for %%F in ("%INSTALLER_DIR%output\ClutchG-Setup-*.exe") do (
    echo  Installer : %%F
    echo  Size      : %%~zF bytes
)

echo.
echo Done.
endlocal
