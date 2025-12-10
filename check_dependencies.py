"""
Скрипт для проверки установки всех необходимых зависимостей
"""
import sys
from pathlib import Path

def check_module(module_name, package_name=None):
    """Проверка наличия модуля"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - НЕ УСТАНОВЛЕН")
        return False

def check_env_file():
    """Проверка наличия .env файла"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env файл найден")
        
        # Проверяем наличие OPENAI_API_KEY
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content and 'sk-' in content:
                print("✅ OPENAI_API_KEY настроен")
                return True
            else:
                print("⚠️ OPENAI_API_KEY не найден или не настроен в .env")
                return False
    else:
        print("❌ .env файл не найден")
        return False

def main():
    print("=" * 60)
    print("🔍 Проверка зависимостей Competition Monitor")
    print("=" * 60)
    
    print("\n📦 Backend зависимости:")
    backend_deps = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("openai", "openai"),
        ("selenium", "selenium"),
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic-settings"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    backend_ok = all(check_module(mod, pkg) for mod, pkg in backend_deps)
    
    print("\n🖥️ Desktop зависимости:")
    desktop_deps = [
        ("PyQt6", "PyQt6"),
        ("requests", "requests"),
        ("PyInstaller", "pyinstaller"),
    ]
    
    desktop_ok = all(check_module(mod, pkg) for mod, pkg in desktop_deps)
    
    print("\n⚙️ Конфигурация:")
    env_ok = check_env_file()
    
    print("\n" + "=" * 60)
    if backend_ok and desktop_ok and env_ok:
        print("✅ Все зависимости установлены и настроены!")
        print("\n🚀 Можно запускать проект:")
        print("   python start_dev.py")
        return 0
    else:
        print("❌ Некоторые зависимости отсутствуют")
        print("\n📝 Для установки выполните:")
        if not backend_ok:
            print("   pip install -r requirements.txt")
        if not desktop_ok:
            print("   pip install -r desktop/requirements.txt")
        if not env_ok:
            print("   Создайте .env файл с OPENAI_API_KEY")
        return 1

if __name__ == "__main__":
    sys.exit(main())
