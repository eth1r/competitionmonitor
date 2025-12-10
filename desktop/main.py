import sys
import json
import subprocess
import time
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QLineEdit, QTextEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from styles import DARK_THEME
from api_client import APIClient

# --- 1. WORKER (Фоновый поток) ---
class AnalysisWorker(QThread):
    # Сигналы: один отправляет результат (словарь), другой ошибку (строка)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.client = APIClient()

    def run(self):
        # Эта часть выполняется в фоне и не тормозит интерфейс
        result = self.client.analyze_site(self.url)
        self.finished_signal.emit(result)

# --- 2. ГЛАВНОЕ ОКНО ---
class CompetitorMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Competitor Monitor")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet(DARK_THEME)
        
        # Backend process
        self.backend_process = None
        
        # Start backend
        self.start_backend()
        
        # Проверяем доступность backend
        self.check_backend_connection()

        self.setup_ui()
    
    def start_backend(self):
        """Запуск backend сервера"""
        try:
            if getattr(sys, 'frozen', False):
                # Если запущено из .exe - используем subprocess для запуска Python скрипта
                self.start_backend_subprocess()
            else:
                # Если запущено из исходников - используем threading
                self.start_backend_thread()
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Ошибка запуска backend", 
                f"Не удалось запустить backend сервер:\n{str(e)}\n\nПриложение может работать некорректно."
            )
    
    def start_backend_subprocess(self):
        """Запуск backend через subprocess (для .exe)"""
        try:
            # Создаем временный Python скрипт для запуска backend
            import tempfile
            
            backend_script = '''
import sys
import os

# Добавляем пути
base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(__file__)
backend_path = os.path.join(base_path, 'backend')
sys.path.insert(0, base_path)
sys.path.insert(0, backend_path)

try:
    import uvicorn
    from backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
except Exception as e:
    print(f"Backend error: {e}")
    import traceback
    traceback.print_exc()
'''
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(backend_script)
                script_path = f.name
            
            # Запускаем как отдельный процесс
            import subprocess
            self.backend_process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ждем запуска
            time.sleep(8)
            
        except Exception as e:
            print(f"Subprocess backend error: {e}")
            # Fallback к threading
            self.start_backend_thread()
    
    def start_backend_thread(self):
        """Запуск backend через threading (для исходников)"""
        try:
            # Определяем путь к backend
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
            
            # Запускаем uvicorn
            import uvicorn
            from threading import Thread
            
            def run_server():
                try:
                    # Импортируем и запускаем app
                    from backend.main import app
                    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
                except Exception as e:
                    print(f"Backend server error: {e}")
            
            # Запускаем в отдельном потоке
            self.backend_thread = Thread(target=run_server, daemon=True)
            self.backend_thread.start()
            
            # Ждем, пока сервер запустится
            time.sleep(5)
            
        except Exception as e:
            print(f"Thread backend error: {e}")
    
    def check_backend_connection(self):
        """Проверка подключения к backend"""
        import requests
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    print(f"Backend connected successfully on attempt {attempt + 1}")
                    return True
            except:
                pass
            
            time.sleep(2)
            print(f"Waiting for backend... attempt {attempt + 1}/{max_attempts}")
        
        # Если не удалось подключиться
        QMessageBox.critical(
            self,
            "Ошибка подключения",
            "Не удалось подключиться к backend серверу.\n\n"
            "Возможные причины:\n"
            "1. Порт 8000 занят другим приложением\n"
            "2. Отсутствуют зависимости\n"
            "3. Проблемы с PyInstaller сборкой\n\n"
            "Попробуйте:\n"
            "- Перезапустить приложение\n"
            "- Закрыть другие приложения на порту 8000\n"
            "- Запустить от имени администратора"
        )
        return False

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # URL
        layout.addWidget(QLabel("🔗 Ссылка на сайт конкурента:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(self.url_input)

        # Инструкция (пока визуальная, backend использует стандартный промпт)
        layout.addWidget(QLabel("📝 Что нужно узнать:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Анализ сильных и слабых сторон (по умолчанию)...")
        self.prompt_input.setMaximumHeight(80)
        layout.addWidget(self.prompt_input)

        # Кнопка
        self.analyze_button = QPushButton("🚀 Запустить анализ")
        self.analyze_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_button)

        # Результат
        layout.addWidget(QLabel("📊 Результат анализа:"))
        self.result_area = QTextEdit()
        self.result_area.setPlaceholderText("Здесь появится ответ от нейросети...")
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        central_widget.setLayout(layout)

    def start_analysis(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите ссылку!")
            return

        # Блокируем кнопку и показываем статус
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Анализирую... (это займет 10-20 сек)")
        self.result_area.setText("Подключение к серверу...\nЗапуск браузера...\nСнятие скриншота...\nОтправка в OpenAI...")

        # Запускаем Worker
        self.worker = AnalysisWorker(url)
        self.worker.finished_signal.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, result):
        # Разблокируем кнопку
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🚀 Запустить анализ")

        if "error" in result:
            self.result_area.setText(f"❌ ОШИБКА:\n{result['error']}")
            if "details" in result:
                self.result_area.append(f"\nДетали:\n{result['details']}")
        else:
            # Парсим успешный ответ
            self.display_success(result)

    def display_success(self, data):
        # Проверяем структуру ответа
        if data.get("success"):
            # Новая структура от API
            result_data = data.get("data", {})
            parsed_data = result_data.get("data", {})
        else:
            # Прямой ответ от /parsedemo
            result_data = data
            parsed_data = data.get("data", {})
        
        # Проверяем статус парсинга
        parsing_status = parsed_data.get("parsing_status", "unknown")
        
        # Формируем красивый текст из JSON
        if parsing_status == "failed":
            output = "❌ ОШИБКА ПАРСИНГА:\n\n"
            output += f"🔗 URL: {result_data.get('url', 'N/A')}\n"
            output += f"❌ Ошибка: {parsed_data.get('error', 'Неизвестная ошибка')}\n"
        else:
            status_icon = "✅" if parsing_status == "success" else "⚠️"
            output = f"{status_icon} РЕЗУЛЬТАТ ПАРСИНГА:\n\n"
            
            output += f"🔗 URL: {result_data.get('url', 'N/A')}\n"
            output += f"📄 Заголовок страницы: {parsed_data.get('page_title', 'N/A')}\n\n"
            
            if parsed_data.get("product_name") and parsed_data['product_name'] != "Не удалось определить":
                output += f"📦 Название: {parsed_data['product_name']}\n\n"
            
            if parsed_data.get("price") and parsed_data['price'] != "Цена не найдена":
                output += f"💰 Цена: {parsed_data['price']}\n\n"
            
            if parsed_data.get("material"):
                output += f"🧵 Материал: {parsed_data['material']}\n\n"
            
            if parsed_data.get("description") and parsed_data['description'] != "Описание не найдено":
                desc = parsed_data['description']
                # Ограничиваем длину описания
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                output += f"📝 Описание:\n{desc}\n\n"
            
            if parsed_data.get("image_url") and parsed_data['image_url'] != "Изображение не найдено":
                output += f"🖼️ Изображение: {parsed_data['image_url']}\n\n"
            
            if parsed_data.get("parsed_at"):
                output += f"⏰ Время парсинга: {parsed_data['parsed_at']}\n"
        
        # Показываем AI анализ, если есть
        ai_analysis = parsed_data.get("ai_analysis")
        if ai_analysis and not ai_analysis.get("error"):
            output += "\n" + "="*50 + "\n"
            output += "🤖 AI АНАЛИЗ КОНКУРЕНТА\n"
            output += "="*50 + "\n\n"
            
            if ai_analysis.get("summary"):
                output += f"📝 РЕЗЮМЕ:\n{ai_analysis['summary']}\n\n"
            
            if ai_analysis.get("strengths"):
                output += "✅ СИЛЬНЫЕ СТОРОНЫ:\n"
                for i, strength in enumerate(ai_analysis['strengths'], 1):
                    output += f"  {i}. {strength}\n"
                output += "\n"
            
            if ai_analysis.get("weaknesses"):
                output += "⚠️ СЛАБЫЕ СТОРОНЫ:\n"
                for i, weakness in enumerate(ai_analysis['weaknesses'], 1):
                    output += f"  {i}. {weakness}\n"
                output += "\n"
            
            if ai_analysis.get("unique_offers"):
                output += "💡 УНИКАЛЬНЫЕ ПРЕДЛОЖЕНИЯ:\n"
                for i, offer in enumerate(ai_analysis['unique_offers'], 1):
                    output += f"  {i}. {offer}\n"
                output += "\n"
            
            if ai_analysis.get("recommendations"):
                output += "🎯 РЕКОМЕНДАЦИИ:\n"
                for i, rec in enumerate(ai_analysis['recommendations'], 1):
                    output += f"  {i}. {rec}\n"
                output += "\n"
        elif ai_analysis and ai_analysis.get("error"):
            output += f"\n⚠️ AI анализ не удался: {ai_analysis.get('note', 'Ошибка OpenAI API')}\n"
        
        # Показываем историю
        history = result_data.get("history", [])
        if history:
            output += f"\n\n📊 История запросов (последние {min(5, len(history))}):\n"
            for i, entry in enumerate(history[:5], 1):
                url_short = entry.get('url', 'N/A')
                if len(url_short) > 50:
                    url_short = url_short[:50] + "..."
                status = entry.get('parsing_status', 'unknown')
                status_icon = "✅" if status == "success" else "⚠️" if status == "partial" else "❌"
                output += f"{i}. {status_icon} {url_short}\n"
        
        self.result_area.setText(output)

def main():
    app = QApplication(sys.argv)
    window = CompetitorMonitorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()