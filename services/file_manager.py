import os
import uuid
from datetime import datetime
from config.settings import DOWNLOAD_PATH

class FileManager:
    def __init__(self):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    def generate_filename(self, prefix: str) -> str:
        """Генерирует уникальное имя файла"""
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(DOWNLOAD_PATH, f"{prefix}_{timestamp}_{unique_id}")

    def cleanup_file(self, filepath: str) -> None:
        """Удаляет файл если он существует"""
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_file_path(self, base_name: str) -> str | None:
        """Ищет файл с разными расширениями"""
        for ext in ['mp4', 'webm', 'mov', 'mkv']:
            path = f"{base_name}.{ext}"
            if os.path.exists(path):
                return path
        return None 