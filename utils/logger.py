import logging
import os
from datetime import datetime

LOG_PATH = "./logs"

os.makedirs(LOG_PATH, exist_ok= True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
    name: str,
    console_level: int = logging.ERROR,
    file_level: int = logging.DEBUG,
    log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    
    logger.addHandler(console_handler)
    
    if not log_file:
        log_file = os.path.join(LOG_PATH, f"{datetime.now().strftime("%Y%m%d")}.log")
    
    file_hanlder = logging.FileHandler(log_file, encoding= "utf-8")
    file_hanlder.setLevel(file_level)
    file_hanlder.setFormatter(DEFAULT_LOG_FORMAT)
    
    logger.addHandler(file_hanlder)
    
    return logger

logger = get_logger("Utils")

if __name__ == '__main__':
    logger.info("测试")