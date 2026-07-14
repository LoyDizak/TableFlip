@echo off
setlocal EnableDelayedExpansion

set "ENTRY_POINT=source\app\main.py"
set "APP_NAME=TableFlip"
set "TARGET_DIR=builds"

:: By default, add the build date to the filename.
:: Pass --no-date to disable it.
set "USE_DATE=1"
if /I "%~1"=="--no-date" set "USE_DATE=0"

if "%USE_DATE%"=="1" (
    for /f "delims=" %%i in ('
        powershell -NoProfile -Command "Get-Date -Format \"dd.MM.yyyy HH-mm\""
    ') do (
        set "TIMESTAMP=%%i"
    )

    set "BUILD_NAME=%APP_NAME% !TIMESTAMP!"
) else (
    set "BUILD_NAME=%APP_NAME%"
)

set "BUILD_FILE=%BUILD_NAME%.exe"

:: Remove old build with the same name
if exist "%TARGET_DIR%\%BUILD_FILE%" del /Q "%TARGET_DIR%\%BUILD_FILE%"

:: Build executable
python3 -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name="%BUILD_NAME%" ^
    "%ENTRY_POINT%"

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

move /Y "dist\%BUILD_FILE%" "%TARGET_DIR%\%BUILD_FILE%" >nul

:: Cleanup
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del "%BUILD_NAME%.spec" 2>nul

echo.
echo Build created:
echo %TARGET_DIR%\%BUILD_FILE%