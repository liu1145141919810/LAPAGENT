import logging
import configparser
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

LOG_LEVEL = cfg.get('logging', 'level', fallback='INFO')
LOG_DIR = cfg.get('logging', 'log_dir', fallback='logs')
LOG_MAX_BYTES = cfg.getint('logging', 'max_bytes', fallback=10485760)  # 10MB
LOG_BACKUP_COUNT = cfg.getint('logging', 'backup_count', fallback=5)

_log_dir_path = os.path.join(_current_dir, LOG_DIR)
os.makedirs(_log_dir_path, exist_ok=True)
_log_file_path = os.path.join(_log_dir_path, 'lapagent.log')

def setup_logger(name:str=None)->logging.Logger:
    # Return a logger instance with the specified configuration
    logger_name = name if name else 'lapagent'
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging,LOG_LEVEL.upper()))

    if logger.handlers:
        return logger
    formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging,LOG_LEVEL.upper()))
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        _log_file_path, maxBytes=LOG_MAX_BYTES, 
        backupCount=LOG_BACKUP_COUNT,encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging,LOG_LEVEL.upper()))
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

#By default
default_logger = setup_logger()