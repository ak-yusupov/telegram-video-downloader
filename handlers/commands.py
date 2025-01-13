from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters
from config.settings import AUTH_CHAT_ID
from config.chat_manager import ChatManager

class BotCommands:
    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager

    def get_handlers(self):
        """Возвращает список всех обработчиков команд для управления чатами"""
        auth_chat_filter = filters.Chat(chat_id=AUTH_CHAT_ID)
        
        return [
            CommandHandler('auth', self.auth),
            CommandHandler('add_allowed_chat', self.add_allowed_chat),
            CommandHandler('remove_allowed_chat', self.remove_allowed_chat),
            CommandHandler('add_blacklist_chat', self.add_blacklist_chat),
            CommandHandler('remove_blacklist_chat', self.remove_blacklist_chat),
        ]

    async def auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка запроса на авторизацию"""
        chat_id = update.message.chat_id

        if self.chat_manager.is_blacklisted_chat(chat_id):
            await update.message.reply_text('Авторизация отклонена')
            return

        if self.chat_manager.is_allowed_chat(chat_id):
            await update.message.reply_text('Вы уже авторизованы')
            return
        
        await update.message.reply_text('Ожидайте подтверждения авторизации')
        
        # Формируем информацию о запросе
        auth_info = (
            f'Запрос авторизации:\n'
            f'Пользователь: @{update.effective_user.username}\n'
            f'User ID: {update.effective_user.id}\n'
            f'Chat ID: {chat_id}\n'
            f'Chat Type: {update.message.chat.type}\n'
            f'Chat Title: {update.message.chat.title if update.message.chat.title else "N/A"}\n\n'
            f'Команды для модерации:'
        )
        
        # Формируем команды для модерации
        commands = [
            f'/add_allowed_chat {chat_id}',
            f'/remove_allowed_chat {chat_id}',
            f'/add_blacklist_chat {chat_id}',
            f'/remove_blacklist_chat {chat_id}'
        ]
        
        # Отправляем информацию модераторам
        await context.bot.send_message(chat_id=AUTH_CHAT_ID, text=auth_info)
        for command in commands:
            await context.bot.send_message(chat_id=AUTH_CHAT_ID, text=command)

    async def add_allowed_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление чата в список разрешенных"""
        if not context.args:
            await update.message.reply_text('Использование: /add_allowed_chat <chat_id>')
            return

        try:
            chat_id = int(context.args[0])
            if self.chat_manager.is_blacklisted_chat(chat_id):
                await update.message.reply_text('Этот чат находится в черном списке')
                return

            self.chat_manager.add_allowed_chat(chat_id)
            await update.message.reply_text(f'Чат {chat_id} добавлен в список разрешенных')
            
            # Уведомляем чат о предоставлении доступа
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Доступ к боту предоставлен'
                )
            except Exception as e:
                await update.message.reply_text(f'Не удалось уведомить чат: {e}')
                
        except ValueError:
            await update.message.reply_text('Неверный формат ID чата')

    async def remove_allowed_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление чата из списка разрешенных"""
        if not context.args:
            await update.message.reply_text('Использование: /remove_allowed_chat <chat_id>')
            return

        try:
            chat_id = int(context.args[0])
            self.chat_manager.remove_allowed_chat(chat_id)
            await update.message.reply_text(f'Чат {chat_id} удален из списка разрешенных')
            
            # Уведомляем чат об отзыве доступа
            try:
                await context.bot.send_message(
                    chat_id=self.chat_manager.normalize_chat_id(chat_id),
                    text='Доступ к боту отозван'
                )
            except Exception:
                pass
                
        except ValueError:
            await update.message.reply_text('Неверный формат ID чата')

    async def add_blacklist_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление чата в черный список"""
        if not context.args:
            await update.message.reply_text('Использование: /add_blacklist_chat <chat_id>')
            return

        try:
            chat_id = int(context.args[0])
            self.chat_manager.add_blacklist_chat(chat_id)
            self.chat_manager.remove_allowed_chat(chat_id)  # Удаляем из разрешенных, если был там
            await update.message.reply_text(f'Чат {chat_id} добавлен в черный список')
            
            # Уведомляем чат о блокировке
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Доступ к боту заблокирован'
                )
            except Exception:
                pass
                
        except ValueError:
            await update.message.reply_text('Неверный формат ID чата')

    async def remove_blacklist_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление чата из черного списка"""
        if not context.args:
            await update.message.reply_text('Использование: /remove_blacklist_chat <chat_id>')
            return

        try:
            chat_id = int(context.args[0])
            self.chat_manager.remove_blacklist_chat(chat_id)
            await update.message.reply_text(f'Чат {chat_id} удален из черного списка')
        except ValueError:
            await update.message.reply_text('Неверный формат ID чата')