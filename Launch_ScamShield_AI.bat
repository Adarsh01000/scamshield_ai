@echo off
title 🛡️ ScamShield AI - Web Application
color 0B

echo ===============================================================================
echo                🛡️ SCAMSHIELD AI: MULTI-AGENT CYBER DEFENSE
echo        AI-Based Multi-Modal Scam Detection & Explainable Risk Assessment
echo ===============================================================================
echo.
echo [1/3] Navigating to ScamShield AI Project root...
cd /d "%~dp0"

echo [2/3] Checking Python virtual environment...
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\venv!
    echo Please ensure the venv directory exists.
    pause
    exit /b 1
)

:: Get Local Network IP for testing on phones/other devices
for /f "tokens=*" %%i in ('.\venv\Scripts\python.exe -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2^>nul') do set NETWORK_IP=%%i
if "%NETWORK_IP%"=="" set NETWORK_IP=10.147.59.3

echo [3/3] Launching ScamShield AI Web Application on Port 8501...
echo.
echo ===============================================================================
echo  💻 THIS LAPTOP URL:          http://localhost:8501
echo  📱 OTHER DEVICES (Wi-Fi):    http://%NETWORK_IP%:8501
echo ===============================================================================
echo  ^> To test on your Mobile Phone or another Laptop:
echo    1. Connect both devices to the same Wi-Fi (or your phone hotspot).
echo    2. Open your phone or other device browser and type: http://%NETWORK_IP%:8501
echo ===============================================================================
echo.
echo Opening default web browser in 3 seconds...
echo Press CTRL+C in this terminal window anytime to stop the server.
echo.

start "" http://localhost:8501
".\venv\Scripts\python.exe" -m streamlit run src/main.py --server.port=8501 --server.address=0.0.0.0 --server.headless=false

pause
