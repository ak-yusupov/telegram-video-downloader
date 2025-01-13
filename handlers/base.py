from collections import OrderedDict
from abc import ABC, abstractmethod
from telegram.ext import MessageHandler, filters
from config.chat_manager import ChatManager

class BaseHandler(ABC):
    def __init__(self, chat_manager: ChatManager):
        self.filter = self._create_filter()
        self.url_to_file_id = OrderedDict()
        self.chat_manager = chat_manager  # Используем переданный экземпляр ChatManager

    @abstractmethod
    def _create_filter(self):
        pass
    
    @abstractmethod
    async def handle(self, update, context):
        pass
    
    def get_handler(self):
        return MessageHandler(self.filter, self.handle) 