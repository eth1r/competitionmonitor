@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 ЗАГРУЗКА НА GITHUB
echo ========================================
echo.

echo 📋 Шаг 1: Инициализация Git...
git init
if errorlevel 1 (
    echo ❌ Ошибка инициализации Git
    pause
    exit /b 1
)
echo ✅ Git инициализирован
echo.

echo 📋 Шаг 2: Добавление файлов...
git add .
if errorlevel 1 (
    echo ❌ Ошибка добавления файлов
    pause
    exit /b 1
)
echo ✅ Файлы добавлены
echo.

echo 📋 Шаг 3: Создание коммита...
git commit -m "Initial commit: Competition Monitor v1.0.7"
if errorlevel 1 (
    echo ❌ Ошибка создания коммита
    pause
    exit /b 1
)
echo ✅ Коммит создан
echo.

echo 📋 Шаг 4: Добавление удаленного репозитория...
git remote add origin https://github.com/eth1r/competitionmonitor.git
if errorlevel 1 (
    echo ⚠️ Remote уже существует, пропускаем...
    git remote set-url origin https://github.com/eth1r/competitionmonitor.git
)
echo ✅ Remote добавлен
echo.

echo 📋 Шаг 5: Отправка на GitHub...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo ❌ Ошибка отправки на GitHub
    echo.
    echo 💡 Возможные причины:
    echo    - Нужна аутентификация (настрой GitHub токен)
    echo    - Репозиторий не пустой (используй git pull --rebase)
    echo.
    pause
    exit /b 1
)
echo.
echo ========================================
echo ✅ УСПЕШНО ЗАГРУЖЕНО НА GITHUB!
echo ========================================
echo.
echo 🌐 Репозиторий: https://github.com/eth1r/competitionmonitor
echo.
echo 📋 СЛЕДУЮЩИЕ ШАГИ:
echo    1. Перейди на GitHub
echo    2. Создай Release (Releases → Create new release)
echo    3. Tag: v1.0.7
echo    4. Загрузи competition-monitor-v1.0.7-windows.zip
echo    5. Опубликуй!
echo.
pause
