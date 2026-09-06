@echo off
title Anti-Sneak Privacy Shield - Installer
echo.
echo ========================================
echo   Installing Anti-Sneak Privacy Shield
echo ========================================
echo.

:: Install Python dependencies
echo [1/2] Installing dependencies...
pip install -r "%~dp0requirements.txt"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Dependency installation failed.
    echo         Make sure Python and pip are installed.
    echo         Download Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/2] Launching Anti-Sneak Shield...
echo.

:: Launch the app
python "%~dp0main.py"

pause
