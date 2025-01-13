import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
AUTH_CHAT_ID = os.getenv('AUTH_CHAT_ID')

MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB

INSTAGRAM_CREDENTIALS = {
    'headers': {
        'User-Agent': os.getenv('USER_AGENT'),
        'X-IG-App-ID': os.getenv('X_IG_APP_ID'),
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.instagram.com",
        "Accept": "*/*",
        "Accept-Language": "ru-RU",
        "Connection": "keep-alive"
    },
    'cookies': {}
}
for item in os.getenv('COOKIES').split(';'):
    item = item.strip()  # убираем пробелы в начале и конце
    if not item:
        continue
    # делим строку по первому '='
    key, value = item.split('=', maxsplit=1)
    INSTAGRAM_CREDENTIALS['cookies'][key] = value

# Регулярные выражения для URL
PATTERNS = {
    'tiktok': r"https?://(\w+\.)?tiktok\.com/[^\s]+",
    "instagram": r"https?://(?:www\.)?instagram\.com(?:/[A-Za-z0-9_.]+)?/reel/[A-Za-z0-9_-]+/?(?:\?[^\s]*)?",
    'youtube': r"https?://(www\.)?youtube\.com/shorts/[^\s]+"
}

# Настройки загрузки
DOWNLOAD_PATH = "downloads" 