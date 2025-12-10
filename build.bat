@echo off
echo ========================================
echo Competition Monitor - Building EXE
echo ========================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Building executable...
python build.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\competitionmonitor.exe
echo.
pause
