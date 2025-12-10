"""
Скрипт для запуска проекта в режиме разработки
Запускает backend сервер и desktop приложение
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Запуск FastAPI backend сервера"""
    print("🚀 Запуск backend сервера...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return backend_process

def start_desktop():
    """Запуск desktop приложения"""
    print("🖥️ Запуск desktop приложения...")
    desktop_process = subprocess.Popen(
        [sys.executable, "desktop/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return desktop_process

def main():
    # Проверяем наличие .env файла
    if not Path(".env").exists():
        print("❌ Файл .env не найден! Создайте его с OPENAI_API_KEY")
        return 1
    
    print("=" * 60)
    print("🎯 Competition Monitor - Development Mode")
    print("=" * 60)
    
    # Запускаем backend
    backend = start_backend()
    
    # Ждем, пока backend запустится
    print("⏳ Ожидание запуска backend (5 секунд)...")
    time.sleep(5)
    
    # Запускаем desktop
    desktop = start_desktop()
    
    print("\n✅ Оба процесса запущены!")
    print("📡 Backend API: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("\n⚠️ Нажмите Ctrl+C для остановки всех процессов\n")
    
    try:
        # Ждем завершения desktop приложения
        desktop.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка процессов...")
    finally:
        # Останавливаем оба процесса
        backend.terminate()
        desktop.terminate()
        
        # Ждем завершения
        backend.wait(timeout=5)
        desktop.wait(timeout=5)
        
        print("✅ Все процессы остановлены")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
