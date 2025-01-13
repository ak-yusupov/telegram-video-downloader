import io
import re
from telegram import Update
from telegram.ext import ContextTypes, filters
from config.settings import PATTERNS
from core.exceptions import DownloadError
from services.downloader import VideoDownloader
from services.file_manager import FileManager
from .base import BaseHandler
from config.chat_manager import ChatManager

class YouTubeHandler(BaseHandler):
    MAX_ENTRIES = 5000  # Максимальное количество сохранённых связок

    def __init__(self, chat_manager: ChatManager):
        self.downloader = VideoDownloader()
        self.file_manager = FileManager()
        
        super().__init__(chat_manager)

    def _create_filter(self):
        return (
            filters.TEXT & 
            ~filters.COMMAND & 
            filters.Regex(PATTERNS['youtube'])
        )

    async def send_and_store_video(self, message, url_no_params):
        filename = self.file_manager.generate_filename("youtube")
        
        try:            
            downloaded_file = await self.downloader.download(url_no_params, filename)
            print('Получено видео из ютуба')
            
            # Отправляем файл напрямую из файловой системы
            sent_message = await message.reply_video(
                video=open(downloaded_file, 'rb'),
                caption="",
                width=1080,
                height=1920
            )
            file_id = sent_message.video.file_id
            
            if url_no_params in self.url_to_file_id:
                del self.url_to_file_id[url_no_params]

            self.url_to_file_id[url_no_params] = file_id

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

        url = re.search(PATTERNS['youtube'], message.text).group(0)   
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


         