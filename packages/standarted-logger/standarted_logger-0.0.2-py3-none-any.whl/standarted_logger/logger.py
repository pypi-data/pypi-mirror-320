import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# TODO: добавить фильтры

class Logger:
    def __init__(self, logger_name, log_level: int=0, log_file: Path = None):
        
        self.logger = logging.getLogger(logger_name)
        # self.logger.addFilter(self.send_to_bot)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s\n')
 
        # file_handler = logging.FileHandler(log_file, encoding='utf-8') 
        if log_file is not None:
            if not log_file.parent.exists():
                log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = TimedRotatingFileHandler(log_file, 'D', interval=3, backupCount=30)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


    def change_log_level(self, new_log_level):
        self.logger.setLevel(new_log_level)

    @staticmethod
    def get_logger(module_name, log_level: int = 0, log_file: Path = None) -> logging.Logger:
        return Logger(module_name, log_level, log_file).logger
