"""日志工具 — 使用 loguru 统一日志输出"""
import sys
from loguru import logger
import config

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <cyan>{module}</cyan> | {message}",
    level="INFO",
)
logger.add(
    config.LOG_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<7} | {module}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
)

def get_logger():
    return logger
