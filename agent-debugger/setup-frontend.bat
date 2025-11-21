@echo off
echo ========================================
echo Setting up Debi AI Agent Frontend
echo ========================================
echo.

cd /d "%~dp0frontend\noha"

echo Installing Node dependencies...
call npm install

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Node dependencies
    echo Please make sure Node.js and npm are installed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Frontend setup complete!
echo ========================================
echo.
echo Run start-frontend.bat to start the dev server
echo.
pause
