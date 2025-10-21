"""
🌌 SarlakBot v3.0 - Logging System
Professional logging with Gen-Z cosmic theme
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json


class CosmicFormatter(logging.Formatter):
    """Custom formatter with cosmic theme"""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add cosmic emoji based on log level
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '✨',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '💥'
        }
        
        emoji = emoji_map.get(record.levelname, '📝')
        color = self.COLORS.get(record.levelname, '')
        
        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create formatted message
        formatted = f"{color}{emoji} [{timestamp}] {record.levelname}: {record.getMessage()}{self.RESET}"
        
        return formatted


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(log_level: str = "INFO", enable_json: bool = False) -> None:
    """
    Setup logging configuration for SarlakBot
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Enable JSON structured logging
    """
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = CosmicFormatter()
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for production
    try:
        file_handler = logging.FileHandler('sarlakbot.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    # Log startup message
    logger.info("🌌 SarlakBot v3.0 logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"JSON logging: {'enabled' if enable_json else 'disabled'}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with cosmic naming
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Cosmic logging decorator
def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"🚀 Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ {func.__name__} failed: {e}")
            raise
    return wrapper


# Async logging decorator
def log_async_function_call(func):
    """Decorator to log async function calls"""
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"🚀 Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"✅ async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ async {func.__name__} failed: {e}")
            raise
    return wrapper


# Global logger instance
logger = get_logger(__name__)




