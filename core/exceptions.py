class DownloadError(Exception):
    """Ошибка при загрузке видео"""
    pass

class FileSizeError(Exception):
    """Ошибка превышения размера файла"""
    pass

class ValidationError(Exception):
    """Ошибка валидации URL"""
    pass 