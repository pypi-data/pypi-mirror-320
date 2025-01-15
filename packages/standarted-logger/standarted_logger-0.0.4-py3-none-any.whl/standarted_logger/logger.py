import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os

class Logger:
    def __init__(self, module_name: str, log_level: int = 10, log_dir: None|Path = None):
        
        self.logger = logging.getLogger(module_name)
        # self.logger.addFilter(self.send_to_bot)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s\n')
 
        # file_handler = logging.FileHandler(log_file, encoding='utf-8') 
        if log_dir is not None:
            file_handler = TimedRotatingFileHandler(os.path.join(log_dir, Path(module_name+".log")), 'D', interval=3, backupCount=30)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def change_log_level(self, new_log_level):
        self.logger.setLevel(new_log_level)

    @staticmethod
    def get_logger(module_name: str, log_level: int = 10, log_dir: None|Path = None) -> logging.Logger:

        if log_dir is not None and log_dir is not None:
            path = Path(log_dir)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

        return Logger(module_name, log_level, log_dir).logger
