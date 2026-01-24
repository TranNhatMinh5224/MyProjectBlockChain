"""
Logging Configuration
Setup logging cho toàn bộ application
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from app.core.config import LOG_LEVEL, LOG_FILE, ENVIRONMENT

# Tạo logs directory nếu chưa có
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

# Định nghĩa format
DETAILED_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Màu sắc cho console (optional)
class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(levelname)s - %(message)s" + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)


def setup_logging():
    """Setup logging configuration"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console Handler (với màu sắc)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    if ENVIRONMENT == "development":
        console_handler.setFormatter(ColoredFormatter())
    else:
        console_handler.setFormatter(SIMPLE_FORMAT)
    
    root_logger.addHandler(console_handler)
    
    # File Handler - Rotating by size (10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(DETAILED_FORMAT)
    root_logger.addHandler(file_handler)
    
    # Error File Handler - Chỉ log errors
    error_log_file = str(Path(LOG_FILE).parent / 'error.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DETAILED_FORMAT)
    root_logger.addHandler(error_handler)
    
    # Tắt log của các thư viện ồn ào
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("=" * 60)
    root_logger.info(f"🚀 Logging initialized - Level: {LOG_LEVEL}")
    root_logger.info(f"📁 Log file: {LOG_FILE}")
    root_logger.info(f"🌍 Environment: {ENVIRONMENT}")
    root_logger.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Usage:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Message")
    """
    return logging.getLogger(name)


# Auto setup khi import
setup_logging()
