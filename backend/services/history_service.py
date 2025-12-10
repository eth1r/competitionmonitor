import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from backend.config import settings
from backend.models.schemas import HistoryItem

class HistoryService:
    def __init__(self):
        # Use absolute path for .exe compatibility (PyInstaller _MEIPASS)
        history_path = settings.history_file
        if not Path(history_path).is_absolute():
            # Store in same directory as executable or current working directory
            import sys
            if getattr(sys, 'frozen', False):
                # Running as .exe - store next to executable
                base_dir = Path(sys.executable).parent
            else:
                # Running as script - store in current directory
                base_dir = Path.cwd()
            self.file_path = base_dir / history_path
        else:
            self.file_path = Path(history_path)
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load(self) -> List[dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, items: List[dict]):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def add_entry(self, req_type: str, req_sum: str, res_sum: str):
        items = self._load()
        
        new_item = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "request_type": req_type,
            "request_summary": req_sum[:1000],
            "response_summary": res_sum[:1000]
        }
        
        # Добавляем в начало списка
        items.insert(0, new_item)
        
        # Ограничиваем длину истории
        if len(items) > settings.max_history_items:
            items = items[:settings.max_history_items]
            
        self._save(items)

    def get_history(self) -> List[HistoryItem]:
        data = self._load()
        return [HistoryItem(**item) for item in data]

    def clear(self):
        self._save([])

history_service = HistoryService()