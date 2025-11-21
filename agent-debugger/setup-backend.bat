@echo off
echo ========================================
echo Setting up Debi AI Agent Backend
echo ========================================
echo.

cd /d "%~dp0backend"

echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Python dependencies
    echo Please make sure Python and pip are installed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a .env file in agent-debugger/ directory
echo 2. Add your GOOGLE_API_KEY to the .env file
echo 3. Run start-backend.bat to start the server
echo.
pause
