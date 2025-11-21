@echo off
echo ========================================
echo Starting Debi AI Agent Backend
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "..\\.env" (
    echo ERROR: .env file not found!
    echo Please create a .env file in agent-debugger/ directory
    echo with your GOOGLE_API_KEY
    echo.
    pause
    exit /b 1
)

echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python api_server.py
