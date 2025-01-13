import io
import re
from urllib.parse import urlparse, urlunparse
from telegram import Update
from telegram.ext import ContextTypes, filters
from config.settings import PATTERNS
from core.exceptions import DownloadError
from services.downloader import VideoDownloader
from services.file_manager import FileManager
from .base import BaseHandler
from config.chat_manager import ChatManager

class TikTokHandler(BaseHandler):
    MAX_ENTRIES = 5000  # Максимальное количество сохранённых связок

    def __init__(self, chat_manager: ChatManager):
        self.downloader = VideoDownloader()
        self.file_manager = FileManager()
        
        super().__init__(chat_manager)

    def _create_filter(self):
        return (
            filters.TEXT & 
            ~filters.COMMAND & 
            filters.Regex(PATTERNS['tiktok'])
        )
        
    def extract_base_tiktok_urls(self, text):
        """
        Извлекает упрощённые TikTok-ссылки из текста.
    
        Параметры:
        text (str): Входной текст для поиска ссылок.
    
        Возвращает:
        list: Список упрощённых TikTok-ссылок.
        """
        # Регулярное выражение для поиска ссылок TikTok
        tiktok_pattern = re.compile(
            r"https?://(?:www\.|vt\.)?tiktok\.com/@[A-Za-z0-9_.]+/(?:(?:photo|video)/)?[A-Za-z0-9_-]+/?(?:\?[^\s]*)?",
            re.IGNORECASE
        )
    
        # Поиск всех совпадений в тексте
        matches = tiktok_pattern.findall(text)
    
        base_urls = []
        for url in matches:
            try:
                # Разбор URL
                parsed_url = urlparse(url)
                
                # Удаление параметров запроса
                base_url = urlunparse(parsed_url._replace(query="", fragment=""))
            
                # Удаление завершающего слэша, если он есть
                if base_url.endswith('/'):
                    base_url = base_url[:-1]
            
                base_urls.append(base_url)
            except Exception as e:
                # В случае ошибки разборки URL, можно логировать её или пропустить
                print(f"Ошибка при обработке URL {url}: {e}")
                continue
    
        return base_urls

    async def send_and_store_video(self, message, url_no_params):
        filename = self.file_manager.generate_filename("tiktok")
        
        try:            
            downloaded_file = await self.downloader.download(url_no_params, filename)
            print('Получено видео из тиктока')
            
            # Отправляем файл напрямую с диска
            sent_message = await message.reply_video(
                    video=open(downloaded_file, 'rb') ,
                    caption="", 
                    width=1080, 
                    height=1920
            )
            
            file_id = sent_message.video.file_id 
            
            # Если URL уже есть в OrderedDict, удаляем его, чтобы обновить порядок
            if url_no_params in self.url_to_file_id:
                del self.url_to_file_id[url_no_params]

            # Добавление новой записи в конец OrderedDict
            self.url_to_file_id[url_no_params] = file_id

            # Если количество записей превышает MAX_ENTRIES, удаляем самые старые
            if len(self.url_to_file_id) > self.MAX_ENTRIES:
                self.url_to_file_id.popitem(last=False)
            
        except DownloadError as e:
            await message.reply_text(f"Не удалось загрузить видео: {str(e)}")
        finally:
            self.file_manager.cleanup_file(downloaded_file)

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        
        if not self.chat_manager.is_allowed_chat(message.chat_id):
            await message.reply_text("Для загрузки видео необходимо авторизоваться. Используйте команду /auth")
            return

        url = re.search(PATTERNS['tiktok'], message.text).group(0)
        url_no_params = re.sub(r'\?.*$', '', url)

        if url_no_params in self.url_to_file_id:
            file_id = self.url_to_file_id[url_no_params]
            try:
                # Отправляем видео используя сохранённый file_id
                await message.reply_video(video=file_id, caption='')
                print("Видео отправлено из памяти.")
            except Exception as e:
                # В случае ошибки, возможно, file_id устарел. Удаляем его и отправляем заново
                print("Не удалось отправить видео из памяти. Попробую загрузить заново.")
                del self.url_to_file_id[url_no_params]
                await self.send_and_store_video(message, url_no_params)
        else:
            await self.send_and_store_video(message, url_no_params)