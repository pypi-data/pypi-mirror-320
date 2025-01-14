import logging
from logging.handlers import TimedRotatingFileHandler

# TODO: принимать APP_DIR как аргумент и писать в файл, если необходимо

class Logger:
    def __init__(self, logger_name, log_file, log_level, APP_DIR=None):
        
        self.logger = logging.getLogger(logger_name)
        # self.logger.addFilter(self.send_to_bot)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s\n')
        light_formatter = logging.Formatter('%(message)s\n')
 
        # file_handler = logging.FileHandler(log_file, encoding='utf-8') 
        file_handler = TimedRotatingFileHandler(log_file, 'D', interval=3, backupCount=30)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(light_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        if app_dir is not None:
            LOGS_FOLDER = APP_DIR / "system_logs"

            path = LOGS_FOLDER / "root.log"
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            root_logger = get_logger("root_logger", path, "DEBUG")

            path = LOGS_FOLDER / "serial.log"
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            serial_logger = get_logger("serial_logger", path, "DEBUG")

            path = LOGS_FOLDER / "ui_logger.log"
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            ui_logger = get_logger("ui_logger", path, "DEBUG")


            path = LOGS_FOLDER / "db_logger.log"
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            db_logger = get_logger("db_logger", path, "DEBUG")
        

    def change_log_level(self, new_log_level):
        self.logger.setLevel(new_log_level)
