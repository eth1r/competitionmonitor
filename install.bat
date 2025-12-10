@echo off
echo ========================================
echo Competition Monitor - Installation
echo ========================================
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing backend dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Installing desktop dependencies...
pip install -r desktop\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install desktop dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Create .env file with your OPENAI_API_KEY
echo 2. Run: start.bat
echo.
pause
