"""
Встроенный backend для desktop приложения
Упрощенная версия без FastAPI для надежности в .exe
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Добавляем пути для импорта backend модулей
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

backend_path = os.path.join(base_path, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if base_path not in sys.path:
    sys.path.insert(0, base_path)


class EmbeddedBackend:
    """Встроенный backend для desktop приложения"""
    
    def __init__(self):
        self.history = []
        
    def analyze_site(self, url: str, analyze: bool = True) -> Dict[str, Any]:
        """Анализ сайта (основная функция)"""
        try:
            # Импортируем функции парсинга
            from backend.services.parsingservice import parse_competitor_data
            from backend.services.openai_service import OpenAIService
            
            # Создаем сервис OpenAI
            openai_service = OpenAIService()
            
            # Парсим сайт
            print(f"Parsing URL: {url}")
            parsed_data = parse_competitor_data(url)
            
            # Добавляем AI анализ если нужно
            if analyze and parsed_data.get("parsing_status") == "success":
                try:
                    print("Starting AI analysis...")
                    ai_analysis = openai_service.analyze_competitor_data(parsed_data)
                    parsed_data["ai_analysis"] = ai_analysis
                except Exception as e:
                    print(f"AI analysis failed: {e}")
                    parsed_data["ai_analysis"] = {
                        "error": True,
                        "note": f"AI анализ не удался: {str(e)}"
                    }
            
            # Добавляем в историю
            history_entry = {
                "url": url,
                "parsing_status": parsed_data.get("parsing_status", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "has_ai_analysis": "ai_analysis" in parsed_data and not parsed_data["ai_analysis"].get("error")
            }
            self.history.insert(0, history_entry)
            
            # Ограничиваем историю
            if len(self.history) > 10:
                self.history = self.history[:10]
            
            # Формируем ответ
            result = {
                "success": True,
                "data": {
                    "url": url,
                    "data": parsed_data,
                    "history": self.history[:5]  # Последние 5 записей
                }
            }
            
            print("Analysis completed successfully")
            return result
            
        except Exception as e:
            print(f"Analysis error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "error": f"Ошибка анализа: {str(e)}",
                "details": f"Проверьте подключение к интернету и корректность URL"
            }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ текста через OpenAI"""
        try:
            from backend.services.openai_service import OpenAIService
            
            openai_service = OpenAIService()
            
            # Создаем данные для анализа
            data = {
                "description": text,
                "product_name": "Текстовый анализ",
                "parsing_status": "success"
            }
            
            analysis = openai_service.analyze_competitor_data(data)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка анализа текста: {str(e)}"
            }
    
    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """Анализ изображения через OpenAI Vision"""
        try:
            from backend.services.openai_service import OpenAIService
            
            openai_service = OpenAIService()
            analysis = openai_service.analyze_image(image_url)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка анализа изображения: {str(e)}"
            }
    
    def get_health(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        return {
            "status": "ok",
            "service": "embedded_backend",
            "timestamp": datetime.now().isoformat()
        }


# Глобальный экземпляр
embedded_backend = EmbeddedBackend()