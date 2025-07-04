@echo off
chcp 65001 > nul
color 0A
setlocal enabledelayedexpansion

REM ===============================
REM  AI Code Context Helper - Build & Release Script
REM ===============================

REM Check pipx
where pipx >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: pipx not found. Please install pipx first.
    echo Run: python -m pip install --user pipx
    echo Then: python -m pipx ensurepath
    pause
    exit /b 1
)

REM Check Poetry
pipx list | findstr poetry >nul
if !errorlevel! neq 0 (
    echo Poetry not found in pipx. Installing Poetry...
    pipx install poetry
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install Poetry!
        pause
        exit /b 1
    )
)

REM Check GitHub CLI
where gh >nul 2>nul
if !errorlevel! neq 0 (
    echo ERROR: GitHub CLI (gh) not found. Please install: https://cli.github.com/
    pause
    exit /b 1
)

REM Install dependencies
cd ..
echo Installing dependencies...
poetry install
if !errorlevel! neq 0 (
    echo ERROR: Dependency installation failed!
    pause
    exit /b 1
)

REM Clean previous build
if exist build rmdir /s /q build

REM Build with cx_Freeze
echo Building with cx_Freeze...
poetry run cxfreeze build
if !errorlevel! neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Find build output directory
cd build
set "srcdir="
for /d %%i in (exe.win-*) do (
    set "srcdir=%%i"
    goto :founddir
)
:founddir
if "!srcdir!"=="" (
    echo ERROR: No exe.win-* directory found in build.
    pause
    exit /b 1
)
echo Found build output directory: !srcdir!

REM Prepare new directory name
set "basename=ai-code-context-helper-master"
set "verstr=!srcdir:exe.=win-!"
set "newdir=!basename!-!verstr!"
echo New directory name will be: !newdir!

REM Copy and rename directory
xcopy "!srcdir!" "!newdir!" /E /I /Y >nul
if not exist "!newdir!" (
    echo ERROR: Failed to copy and rename build directory.
    pause
    exit /b 1
)

REM Zip the directory
echo Zipping directory...
powershell -Command "Compress-Archive -Path '!newdir!\*' -DestinationPath '!newdir!.zip'"
if not exist "!newdir!.zip" (
    echo ERROR: Failed to create zip archive.
    pause
    exit /b 1
)

REM Prompt for version
echo.
set /p version=Please enter release version (e.g. v1.0.0):
if "!version!"=="" (
    echo ERROR: No version entered.
    pause
    exit /b 1
)

REM Move zip to project root for release
move /Y "!newdir!.zip" ..\!newdir!.zip >nul
cd ..

REM Create GitHub release and upload zip
echo Creating GitHub release...
gh release create !version! "!newdir!.zip" --title "!version!" --notes "Auto release !version!"
if !errorlevel! neq 0 (
    echo ERROR: Failed to create GitHub release or upload asset.
    pause
    exit /b 1
)

REM Clean up
cd build
rmdir /s /q "!newdir!"
cd ..
del /q "!newdir!.zip"

endlocal

echo Release completed successfully!
pause