@echo off
title 🛡️ ScamShield AI - REST API Server
color 0A

echo ===============================================================================
echo                🛡️ SCAMSHIELD AI: REST API SERVER (FASTAPI)
echo ===============================================================================
echo.
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\venv!
    pause
    exit /b 1
)

echo Starting FastAPI server at http://127.0.0.1:8000
echo Interactive API Swagger Docs: http://127.0.0.1:8000/docs
echo.
start "" http://127.0.0.1:8000/docs
".\venv\Scripts\python.exe" -m uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload

pause
