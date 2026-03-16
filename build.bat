@echo off
setlocal enabledelayedexpansion

set "ENTRY_POINT=source\app\main.py"
set "APP_NAME=TableFlip"
set "TARGET_DIR=builds"
set "BUILD_NAME=%APP_NAME%.exe"

python3 -m PyInstaller --onefile --noconsole --name="%APP_NAME%" %ENTRY_POINT%
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM Change file name if it already exists
set "NEW_NAME=%BUILD_NAME%"
set /A count=1
:check_exists
if exist "%TARGET_DIR%\!NEW_NAME!" (
    set "BASENAME=%APP_NAME% (!count!)"
    set "NEW_NAME=!BASENAME!.exe"
    set /A count+=1
    goto check_exists
)

move /Y "dist\%BUILD_NAME%" "%TARGET_DIR%\!NEW_NAME!"

rmdir /S /Q build
rmdir /S /Q dist
del "%APP_NAME%.spec"

pause
