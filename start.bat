@echo off
echo ========================================
echo Competition Monitor - Starting
echo ========================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env file with OPENAI_API_KEY
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking dependencies...
python check_dependencies.py
if errorlevel 1 (
    echo.
    echo ERROR: Some dependencies are missing
    echo Please run install.bat
    pause
    exit /b 1
)

echo.
echo Starting application...
python start_dev.py

pause
