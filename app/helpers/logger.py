import logging
from logging.handlers import RotatingFileHandler
import sys


class Log:

    def __init__(self, log_file: str = 'app.log'):
        log_format = '%(asctime)s - %(levelname)s - %(message)s'

        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))

        file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def send_log(self, message: str):
        """Logs an informational message"""
        self.logger.info(message)

    def send_debug(self, message: str):
        """Logs a debug message (for troubleshooting)"""
        self.logger.debug(message)

    def send_warning(self, message: str):
        """Logs a warning message"""
        self.logger.warning(message)

    def send_error(self, message: str):
        """Logs an error message"""
        self.logger.error(message)

    def send_critical(self, message: str):
        """Logs a critical error message (high severity)"""
        self.logger.critical(message)


logger = Log()
