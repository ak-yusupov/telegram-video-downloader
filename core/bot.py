from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from handlers import TikTokHandler, InstagramHandler, YouTubeHandler
from handlers.commands import BotCommands
from config.settings import BOT_TOKEN
from config.chat_manager import ChatManager

class VideoDownloaderBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Создаем единый экземпляр ChatManager
        chat_manager = ChatManager()

        bot_commands = BotCommands(chat_manager)

        # Регистрация обработчиков команд управления чатами
        for handler in bot_commands.get_handlers():
            self.app.add_handler(handler)

        # Регистрация обработчиков отправки видео в чаты
        self.app.add_handler(TikTokHandler(chat_manager).get_handler())
        self.app.add_handler(InstagramHandler(chat_manager).get_handler())
        self.app.add_handler(YouTubeHandler(chat_manager).get_handler())

    
    def run(self):
        print("Бот запущен. Нажмите Ctrl+C для остановки.")
        self.app.run_polling() 