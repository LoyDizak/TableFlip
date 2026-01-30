@echo off
setlocal enabledelayedexpansion

set "ENTRY_POINT=Source\Front.py"
set "APP_NAME=DOCX Analyze v2"
set "TARGET_DIR=Builds"

set "BUILD_NAME=%APP_NAME%.exe"

REM =========================
REM Сборка
REM =========================
python3 -m PyInstaller --onefile --noconsole --name="%APP_NAME%" %ENTRY_POINT%

REM =========================
REM Создание папки, если нет
REM =========================
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM =========================
REM Находим имя для нового файла
REM =========================
set "NEW_NAME=%BUILD_NAME%"
set /A count=1

:check_exists
if exist "%TARGET_DIR%\!NEW_NAME!" (
    REM Берём имя без расширения и формируем с номером
    set "BASENAME=%APP_NAME% (!count!)"
    set "NEW_NAME=!BASENAME!.exe"
    set /A count+=1
    goto check_exists
)

REM =========================
REM Перемещаем файл в папку Builds
REM =========================
move /Y "dist\%BUILD_NAME%" "%TARGET_DIR%\!NEW_NAME!"

REM =========================
REM Удаляем временные папки/файлы
REM =========================
rmdir /S /Q build
rmdir /S /Q dist
del "%APP_NAME%.spec"

pause
