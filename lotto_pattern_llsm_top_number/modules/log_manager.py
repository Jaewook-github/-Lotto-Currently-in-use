# LogManager 클래스
# modules/log_manager.py
import logging
import logging.handlers


class LogManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정 (파일 회전 기능 포함)"""
        log_file = self.file_manager.get_new_log_file()
        self.logger = logging.getLogger('LottoPrediction')
        self.logger.setLevel(logging.DEBUG)  # 디버그 레벨까지 기록

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        self.logger.handlers = []
        self.logger.addHandler(file_handler)

    def log_info(self, message: str):
        """정보 로그 기록"""
        self.logger.info(message)

    def log_error(self, message: str, exc_info=None):
        """에러 로그 기록"""
        self.logger.error(message, exc_info=exc_info)

    def log_debug(self, message: str):
        """디버그 로그 기록"""
        self.logger.debug(message)