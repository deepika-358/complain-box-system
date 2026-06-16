@echo off
title Complain Box — Backend Server
color 0A
echo.
echo  =====================================================
echo    COMPLAIN BOX SYSTEM — Starting Backend...
echo  =====================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Go to backend folder
cd /d "%~dp0backend"

:: Install dependencies if not already installed
echo  [1/2] Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo  [2/2] Starting Flask server...
echo.
echo  =====================================================
echo    API Running at: http://localhost:5000
echo    Admin Login:    shine / 262425
echo    Open frontend\index.html in your browser!
echo  =====================================================
echo.

python app.py

pause
