@echo off
title Building CpFlight_Controller.exe

echo.
echo ============================================
echo   Building CpFlight_Controller...
echo ============================================
echo.

REM Clean previous build/dist folders
if exist build (
    echo Removing old build folder...
    rmdir /s /q build
)
if exist dist (
    echo Removing old dist folder...
    rmdir /s /q dist
)

if exist CpFlight_Controller.spec (
    echo Removing old spec file...
    del CpFlight_Controller.spec
)

echo Running PyInstaller...
py gen_version.py
pyinstaller --onefile --noconsole --name CpFlight_Controller main.py --hidden-import SimConnect --hidden-import scapi --add-binary ".venv\Lib\site-packages\SimConnect\SimConnect.dll;SimConnect" --icon=resources/butzy.ico --add-data "resources/butzy.ico;resources"

echo.
echo Copying settings.json and config folder to dist...
copy /Y .\resources\settings_template.json dist\settings.json
xcopy config dist\config\ /E /I /Y

echo.
echo ============================================
echo   Build completed!
echo   Your file is here: dist\CpFlight_Controller.exe
echo   Config files have been copied next to the EXE.
echo ============================================
echo.