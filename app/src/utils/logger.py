import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name: str, log_file: str = "logs/app.log", level=logging.DEBUG):
    base_dir = os.path.dirname(log_file)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
        print('mkdir success')

    log_format = "%(asctime)s - %(name)-15s - %(levelname)-8s - LINE:%(lineno)d- %(message)s"
    formatter = logging.Formatter(log_format)

    # 創建日誌處理器，每天創建一個新檔案
    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 創建終端輸出處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 防止多次添加 handler
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger