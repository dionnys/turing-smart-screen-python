@echo off
cd /d "%~dp0"
echo =======================================================
echo Building Turing Smart Screen - Deep Clean System
echo =======================================================
echo.

echo [0/2] Cleaning previous build folders...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist installer_output rd /s /q installer_output

echo.
echo [1/2] Compiling Python executable with PyInstaller...
call venv\Scripts\activate.bat
pyinstaller --clean -y turing-system-monitor.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [1.5/2] Copying required resources to dist folder...
xcopy /E /I /Y "res" "dist\turing-system-monitor\res"
xcopy /E /I /Y "locales" "dist\turing-system-monitor\locales"
xcopy /E /I /Y "external" "dist\turing-system-monitor\external"
copy /Y "config.yaml" "dist\turing-system-monitor\config.yaml"

echo.
echo [2/2] Packing installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" TURZX_Installer.iss

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Inno Setup failed! Ensure Inno Setup 6 is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =======================================================
echo BUILD SUCCESSFUL!
echo The new installer is located in the "installer_output" folder.
echo =======================================================
pause
