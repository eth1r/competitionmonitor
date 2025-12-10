"""
Упрощенная версия desktop приложения без backend сервера
Все функции встроены напрямую
"""

import sys
import os
import json
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QLineEdit, QTextEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Добавляем пути для импорта
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Импортируем стили
try:
    from styles import DARK_THEME
except ImportError:
    DARK_THEME = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QPushButton {
        background-color: #404040;
        border: 1px solid #555555;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #505050;
    }
    QLineEdit, QTextEdit {
        background-color: #404040;
        border: 1px solid #555555;
        padding: 4px;
        border-radius: 4px;
    }
    """


class SimpleAnalysisWorker(QThread):
    """Простой worker для анализа без backend сервера"""
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        """Выполняем анализ напрямую"""
        try:
            result = self.analyze_site_direct(self.url)
            self.finished_signal.emit(result)
        except Exception as e:
            self.finished_signal.emit({
                "error": f"Ошибка анализа: {str(e)}"
            })
    
    def analyze_site_direct(self, url):
        """Прямой анализ сайта без API"""
        try:
            # Импортируем функцию парсинга
            from backend.services.parsingservice import parse_competitor_data
            
            # Парсим сайт
            parsed_data = parse_competitor_data(url)
            
            # Пробуем добавить AI анализ
            try:
                from backend.services.openai_service import OpenAIService
                openai_service = OpenAIService()
                
                # Проверяем, что parsed_data это словарь, а не строка
                if isinstance(parsed_data, dict) and not parsed_data.get("error"):
                    ai_analysis = openai_service.analyze_competitor_data(parsed_data)
                    parsed_data["ai_analysis"] = ai_analysis
                else:
                    parsed_data["ai_analysis"] = {
                        "error": True,
                        "note": "AI анализ недоступен: ошибка парсинга"
                    }
            except Exception as e:
                print(f"AI analysis failed: {e}")
                parsed_data["ai_analysis"] = {
                    "error": True,
                    "note": f"AI анализ недоступен: {str(e)}"
                }
            
            # Формируем ответ
            return {
                "success": True,
                "data": {
                    "url": url,
                    "data": parsed_data
                }
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка парсинга: {str(e)}",
                "details": "Проверьте подключение к интернету и корректность URL"
            }


class SimpleCompetitorMonitorApp(QMainWindow):
    """Упрощенное приложение без backend сервера"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Competitor Monitor (Simple)")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet(DARK_THEME)
        
        self.setup_ui()

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
        self.result_area.setText("Запуск браузера...\nПарсинг страницы...\nОтправка в OpenAI...")

        # Запускаем Worker
        self.worker = SimpleAnalysisWorker(url)
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
        """Отображение успешного результата"""
        try:
            result_data = data.get("data", {})
            parsed_data = result_data.get("data", {})
            
            # Проверяем статус парсинга
            parsing_status = parsed_data.get("parsing_status", "unknown")
            
            if parsing_status == "failed":
                output = "❌ ОШИБКА ПАРСИНГА:\n\n"
                output += f"🔗 URL: {result_data.get('url', 'N/A')}\n"
                output += f"❌ Ошибка: {parsed_data.get('error', 'Неизвестная ошибка')}\n"
            else:
                status_icon = "✅" if parsing_status == "success" else "⚠️"
                output = f"{status_icon} РЕЗУЛЬТАТ ПАРСИНГА:\n\n"
                
                output += f"🔗 URL: {result_data.get('url', 'N/A')}\n"
                output += f"📄 Заголовок: {parsed_data.get('page_title', 'N/A')}\n\n"
                
                if parsed_data.get("product_name") and parsed_data['product_name'] != "Не удалось определить":
                    output += f"📦 Название: {parsed_data['product_name']}\n\n"
                
                if parsed_data.get("price") and parsed_data['price'] != "Цена не найдена":
                    output += f"💰 Цена: {parsed_data['price']}\n\n"
                
                if parsed_data.get("description") and parsed_data['description'] != "Описание не найдено":
                    desc = parsed_data['description']
                    if len(desc) > 300:
                        desc = desc[:300] + "..."
                    output += f"📝 Описание:\n{desc}\n\n"
            
            # AI анализ
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
                
                if ai_analysis.get("recommendations"):
                    output += "🎯 РЕКОМЕНДАЦИИ:\n"
                    for i, rec in enumerate(ai_analysis['recommendations'], 1):
                        output += f"  {i}. {rec}\n"
                    output += "\n"
            elif ai_analysis and ai_analysis.get("error"):
                output += f"\n⚠️ AI анализ: {ai_analysis.get('note', 'Недоступен')}\n"
            
            self.result_area.setText(output)
            
        except Exception as e:
            self.result_area.setText(f"❌ Ошибка отображения результата: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = SimpleCompetitorMonitorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()