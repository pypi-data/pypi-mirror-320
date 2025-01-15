"""
Logging configuration for YouTube Transcript Generator.
"""
import sys
from pathlib import Path
from loguru import logger
from .config import get_settings

settings = get_settings()


def setup_logger():
    """Configure logging settings."""
    # Remove default logger
    logger.remove()
    
    # Determine log path
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    # Configure formatters
    format_stdout = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                    "<level>{message}</level>")
    
    format_file = ("{time:YYYY-MM-DD HH:mm:ss} | "
                   "{level: <8} | "
                   "{name}:{function}:{line} | "
                   "{message}")
    
    # Add handlers
    # Console handler
    logger.add(
        sys.stdout,
        format=format_stdout,
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # File handler for errors
    logger.add(
        log_path / "error.log",
        format=format_file,
        level="ERROR",
        rotation="1 week",
        retention="1 month",
        compression="zip"
    )
    
    # File handler for all logs
    logger.add(
        log_path / "debug.log",
        format=format_file,
        level=settings.LOG_LEVEL,
        rotation="1 day",
        retention="1 week",
        compression="zip"
    )
    
    # Add context to all logs
    logger.configure(
        extra={
            "app_name": "youtube_transcript_generator",
            "environment": "development" if settings.DEBUG else "production"
        }
    )
    
    return logger


# Initialize logger
logger = setup_logger()