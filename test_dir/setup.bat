@echo off
REM Noha Development Environment Setup Script for Windows

echo ========================================
echo Noha Interview Dashboard Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    exit /b 1
)

echo [OK] Python and Node.js are installed
echo.

REM Setup Backend
echo ========================================
echo Setting up Backend...
echo ========================================
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [ACTION REQUIRED] Please edit backend\.env and configure your API keys
)

cd..
echo [OK] Backend setup complete!
echo.

REM Setup Frontend
echo ========================================
echo Setting up Frontend...
echo ========================================
cd frontend\noha

echo Installing Node dependencies...
call npm install

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
)

cd..\..
echo [OK] Frontend setup complete!
echo.

REM Final Instructions
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Setup PostgreSQL Database:
echo    - Create database: createdb noha_db
echo    - Run schema: psql -d noha_db -f database\schema.sql
echo.
echo 2. Start Redis (optional):
echo    - Install and start Redis server
echo.
echo 3. Configure Backend:
echo    - Edit backend\.env with your configuration
echo    - Add DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
echo.
echo 4. Start Backend:
echo    - cd backend
echo    - venv\Scripts\activate
echo    - python main.py
echo.
echo 5. Start Frontend:
echo    - cd frontend\noha
echo    - npm run dev
echo.
echo 6. Access Application:
echo    - Frontend: http://localhost:5173
echo    - Backend: http://localhost:8000
echo    - API Docs: http://localhost:8000/api/docs
echo.
echo Default login: admin@noha.com / Admin@123
echo.
echo ========================================
pause
