@echo off
title Building CpFlight_Controller.exe

echo.
echo ============================================
echo   Building CpFlight_Controller...
echo ============================================
echo.

REM Clean previous build/dist folders
if exist build (
    echo 🧹 Removing old build folder...
    rmdir /s /q build
)
if exist dist (
    echo 🧹 Removing old dist folder...
    rmdir /s /q dist
)

echo Running PyInstaller...
pyinstaller --onefile --noconsole --add-data "config;config" --name CpFlight_Controller main.py --hidden-import SimConnect --hidden-import scapi

echo.
echo ============================================
echo   Build completed!
echo   Your file is here: dist\CpFlight_Controller.exe
echo ============================================
echo.

pause