import requests
import sys
import os

class APIClient:
    def __init__(self):
        # Адрес нашего локального сервера (FastAPI)
        self.base_url = "http://127.0.0.1:8000"
        self.use_embedded = False
        
        # Проверяем, запущено ли из .exe
        if getattr(sys, 'frozen', False):
            # Пробуем подключиться к серверу, если не получается - используем встроенный backend
            try:
                response = requests.get(f"{self.base_url}/health", timeout=3)
                if response.status_code != 200:
                    self.use_embedded = True
            except:
                self.use_embedded = True
                print("Using embedded backend (server not available)")

    def analyze_site(self, url: str):
        """Отправляет URL на парсинг и анализ"""
        if self.use_embedded:
            return self._analyze_site_embedded(url)
        else:
            return self._analyze_site_server(url)
    
    def _analyze_site_server(self, url: str):
        """Анализ через FastAPI сервер"""
        endpoint = f"{self.base_url}/parsedemo"
        
        try:
            # Отправляем GET запрос с URL параметром
            response = requests.get(endpoint, params={"url": url}, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "data": data}
            else:
                return {"error": f"Ошибка сервера: {response.status_code}", "details": response.text}
                
        except requests.exceptions.ConnectionError:
            # Переключаемся на встроенный backend
            print("Server connection failed, switching to embedded backend")
            self.use_embedded = True
            return self._analyze_site_embedded(url)
        except Exception as e:
            return {"error": f"Произошла ошибка: {str(e)}"}
    
    def _analyze_site_embedded(self, url: str):
        """Анализ через встроенный backend"""
        try:
            from .embedded_backend import embedded_backend
            return embedded_backend.analyze_site(url)
        except Exception as e:
            return {"error": f"Ошибка встроенного backend: {str(e)}"}