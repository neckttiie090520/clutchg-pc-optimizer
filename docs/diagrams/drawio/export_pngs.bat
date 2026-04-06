@echo off
setlocal
set "DRAWIO=C:\Program Files\draw.io\draw.io.exe"
set "DIR=C:\Users\nextzus\Documents\thesis\bat\docs\diagrams"

for %%f in ("%DIR%\*.drawio") do (
    set "OUT=%%~dpnf.png"
    "%DRAWIO%" --export --format png --scale 2 --border 20 --output "%%~dpnf.png" "%%f" 2>nul
    if exist "%%~dpnf.png" (
        echo OK: %%~nxf
    ) else (
        echo FAIL: %%~nxf
    )
)
echo Done.
