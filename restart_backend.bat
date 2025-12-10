@echo off
echo ========================================
echo Перезапуск Backend сервера
echo ========================================
echo.

echo Останавливаем старый процесс на порту 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Убиваем процесс %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo Ждем 2 секунды...
timeout /t 2 /nobreak >nul

echo.
echo Запускаем новый backend...
start "Backend Server" cmd /k "venv\Scripts\activate && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo ========================================
echo Backend перезапущен!
echo ========================================
echo.
echo Проверьте: http://127.0.0.1:8000/docs
echo.
pause
