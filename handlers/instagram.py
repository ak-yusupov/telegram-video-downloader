import re
import requests
from telegram import Update
from telegram.ext import ContextTypes, filters
from config.settings import PATTERNS, INSTAGRAM_CREDENTIALS
from .base import BaseHandler
from services.downloader import VideoDownloader
from services.file_manager import FileManager
from config.chat_manager import ChatManager


class InstagramHandler(BaseHandler):
    MAX_ENTRIES = 5000  # Максимальное количество сохранённых связок
    
    def __init__(self, chat_manager: ChatManager):
        self.downloader = VideoDownloader()
        self.file_manager = FileManager()
        super().__init__(chat_manager)

    def _create_filter(self):
        return filters.TEXT & ~filters.COMMAND & filters.Regex(PATTERNS['instagram'])

    def get_id(self, url: str) -> str:
        """Извлекает идентификатор (p/reels/reel/stories) из ссылки."""
        match = re.search(
            r"instagram\.com/(?:[A-Za-z0-9_.]+/)?(p|reels|reel|stories)/([A-Za-z0-9-_]+)",
            url
        )
        return match.group(2) if match else None
    
    def get_video_url(self, url: str) -> str | None:
        """
        Пытается достать прямую ссылку на видео из Instagram, используя
        внутренние API (подстановка __a=1&__d=dis).
        """
        ig_id = self.get_id(url)
        if not ig_id:
            return None

        params = {
        "__a": "1",
        "__d": "dis"
        }

        try:
            response = requests.get(
                f"https://www.instagram.com/p/{ig_id}",
                headers=INSTAGRAM_CREDENTIALS['headers'],
                cookies=INSTAGRAM_CREDENTIALS['cookies'],
                params=params   
            )
            response.raise_for_status()
            
            json_data = response.json()
            items = json_data.get('items', [{}])
            if not items:
                return None

            video_versions = items[0].get('video_versions')
            if not video_versions:
                return None
            return video_versions[0].get('url')

        except (requests.RequestException, ValueError, IndexError) as e:
            print(f"Ошибка при получении URL видео: {str(e)}")
            return None

    async def send_and_store_video(self, message, url_no_params: str):
        """
        Сначала пытаемся получить прямую ссылку на видео через get_video_url.
        Если ссылка получена, пытаемся её скачать и отправить. Если не удалось,
        отсылаем сообщение об ошибке.
        """
        print('Пробуем получить ссылку на видео из инсты через API')
        video_url = self.get_video_url(url_no_params)
        if not video_url:
            try:
                # Если ссылка получена, пытаемся скачать файл и отправить
                print("Не удалось получить ссылку на видео по API. Качаем видео через библиотеку")
                filename = self.file_manager.generate_filename("instagram")
                downloaded_file = await self.downloader.download(url_no_params, filename)
                sent_message = await message.reply_video(
                    video=downloaded_file,
                    caption="",
                    width=1080,
                    height=1920
                )
            except Exception as e:
                print(f"Ошибка при скачивании/отправке файла: {str(e)}")
                return
            finally:
                # В любом случае чистим временный файл
                self.file_manager.cleanup_file(filename)
            
        else:
            try:
                print(f"Ссылка на видео по API получена")
                sent_message = await message.reply_video(
                    video=video_url,
                    caption="",
                        width=1080,
                        height=1920
                    )
            except Exception as e:
                print(f"Ошибка при отправке видео: {str(e)}")
                return

        # Сохраняем file_id для кэширования
        file_id = sent_message.video.file_id
        if url_no_params in self.url_to_file_id:
            del self.url_to_file_id[url_no_params]
        self.url_to_file_id[url_no_params] = file_id
        
        # Если кэш слишком большой — подчищаем
        if len(self.url_to_file_id) > self.MAX_ENTRIES:
            self.url_to_file_id.popitem(last=False)

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not self.chat_manager.is_allowed_chat(message.chat_id):
            await message.reply_text("Для загрузки видео необходимо авторизоваться. Используйте команду /auth")
            return
        
        # Проверяем, есть ли URL из Instagram в тексте
        url_match = re.search(PATTERNS['instagram'], message.text)
        if not url_match:
            return
        
        # Очищаем URL от GET-параметров, чтобы у нас был базовый ключ для кэша
        url_no_params = re.sub(r'\?.*$', '', url_match.group(0))
        
        # Если уже загружали видео по этому URL, пробуем сразу отправить по file_id
        if url_no_params in self.url_to_file_id:
            file_id = self.url_to_file_id[url_no_params]
            try:
                await message.reply_video(video=file_id, caption='')
                print("Видео отправлено из памяти.")
            except Exception as e:
                print(f"Не удалось отправить видео из памяти: {str(e)}. Пробуем загрузить заново.")
                del self.url_to_file_id[url_no_params]
                await self.send_and_store_video(message, url_no_params)
        else:
            # Если в кэше нет, делаем новую загрузку
            await self.send_and_store_video(message, url_no_params)