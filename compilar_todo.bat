@echo off
echo =======================================================
echo Building Turing Smart Screen - Latest Version
echo =======================================================
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
