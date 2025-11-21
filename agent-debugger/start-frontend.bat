@echo off
echo ========================================
echo Starting Debi AI Agent Frontend
echo ========================================
echo.

cd /d "%~dp0frontend\noha"

echo Starting development server...
echo Frontend will be available at http://localhost:5173
echo Press Ctrl+C to stop the server
echo.

call npm run dev
