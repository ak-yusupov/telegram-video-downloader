import yt_dlp
from config.settings import MAX_FILE_SIZE
from core.exceptions import DownloadError, FileSizeError

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'mp4',
            'max_filesize': MAX_FILE_SIZE
        }

    async def download(self, url: str, output_path: str) -> str:
        """
        Загружает видео по URL
        Returns: путь к загруженному файлу
        """
        final_path = f"{output_path}.mp4"
        try:
            opts = {
                **self.ydl_opts,
                'format': 'mp4',
                'max_filesize': MAX_FILE_SIZE,
                'outtmpl': f'{output_path}.%(ext)s'
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url]) 
            
            return final_path
            
        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(f"Ошибка загрузки: {str(e)}")
        except Exception as e:
            raise DownloadError(f"Неожиданная ошибка: {str(e)}")