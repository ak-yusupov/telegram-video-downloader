import json
import os
from typing import Set

class ChatManager:
    def __init__(self):
        self.allowed_chats: Set[int] = set()
        self.blacklist_chats: Set[int] = set()
        self.file_path_allowed = "config/allowed_chats.json"
        self.file_path_blacklist = "config/blacklist_chats.json"
        self.load_chats()
    
    def load_chats(self) -> None:
        """Загружает разрешенные и заблокированные чаты из файлов"""
        self.allowed_chats = self._load_from_file(
            self.file_path_allowed, "allowed_chats"
        )
        self.blacklist_chats = self._load_from_file(
            self.file_path_blacklist, "blacklist"
        )

    def save_chats(self) -> None:
        """Сохраняет текущие списки чатов в файлы"""
        self._save_to_file(
            self.file_path_allowed, 
            {"allowed_chats": list(self.allowed_chats)}
        )
        self._save_to_file(
            self.file_path_blacklist, 
            {"blacklist": list(self.blacklist_chats)}
        )

    def add_allowed_chat(self, chat_id: int) -> None:
        """Добавляет чат в список разрешенных"""
        self.allowed_chats.add(chat_id)
        self.save_chats()

    def remove_allowed_chat(self, chat_id: int) -> None:
        """Удаляет чат из списка разрешенных"""
        self.allowed_chats.discard(chat_id)
        self.save_chats()

    def add_blacklist_chat(self, chat_id: int) -> None:
        """Добавляет чат в черный список"""
        self.blacklist_chats.add(chat_id)
        self.save_chats()

    def remove_blacklist_chat(self, chat_id: int) -> None:
        """Удаляет чат из черного списка"""
        self.blacklist_chats.discard(chat_id)
        self.save_chats()

    def _load_from_file(self, file_path: str, key: str) -> Set[int]:
        """
        Загружает данные из JSON файла
        
        Args:
            file_path: путь к файлу
            key: ключ для получения данных из JSON
        
        Returns:
            Set[int]: множество ID чатов
        """
        if not os.path.exists(file_path):
            return set()
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return set(data.get(key, []))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return set()

    def _save_to_file(self, file_path: str, data: dict) -> None:
        """
        Сохраняет данные в JSON файл
        
        Args:
            file_path: путь к файлу
            data: данные для сохранения
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении в файл {file_path}: {e}")

    def is_allowed_chat(self, chat_id: int) -> bool:
        """Проверяет, находится ли чат в списке разрешенных"""
        return chat_id in self.allowed_chats

    def is_blacklisted_chat(self, chat_id: int) -> bool:
        """Проверяет, находится ли чат в черном списке"""
        return chat_id in self.blacklist_chats