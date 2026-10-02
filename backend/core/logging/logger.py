import logging
from logging.handlers import RotatingFileHandler
import os
import re
import sys

# ANSI Color codes for console output
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "DEBUG": "\033[36m",      # Cyan
    "INFO": "\033[32m",       # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "CRITICAL": "\033[1;31m", # Bold Red
    "STATUS_2XX": "\033[92m", # Bright Green
    "STATUS_3XX": "\033[96m", # Bright Cyan
    "STATUS_4XX": "\033[93m", # Bright Yellow / Orange
    "STATUS_5XX": "\033[91m", # Bright Red
    "NAME": "\033[34m",       # Blue
    "TIME": "\033[90m",       # Grey
}

class ColoredConsoleFormatter(logging.Formatter):
    """
    Console formatter for Development with distinct ANSI colors for:
    - Log levels (DEBUG, INFO, WARN, ERROR, CRITICAL)
    - HTTP status codes (2xx Green, 3xx Cyan, 4xx Yellow, 5xx Red)
    - Timestamp and Logger name
    """
    
    # Regex to catch status codes like "Status: 404", "HTTP/1.1 404", " 404 Not Found"
    STATUS_REGEX = re.compile(r'\b(Status:\s*|HTTP/\d\.\d\s+)?([1-5]\d{2})(\s+[A-Za-z\s]+)?\b')

    def format(self, record: logging.LogRecord) -> str:
        level_name = record.levelname
        level_color = COLORS.get(level_name, COLORS["RESET"])
        reset = COLORS["RESET"]
        
        # Colorized time & level
        time_str = f"{COLORS['TIME']}{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}{reset}"
        lvl_str = f"{level_color}{level_name:<8}{reset}"
        name_str = f"{COLORS['NAME']}{record.name}{reset}"
        
        # Format base message
        message = record.getMessage()
        
        # Highlight HTTP Status Codes in message if present
        def colorize_status(match):
            prefix = match.group(1) or ""
            code = match.group(2)
            suffix = match.group(3) or ""
            if code.startswith("2"):
                color = COLORS["STATUS_2XX"]
            elif code.startswith("3"):
                color = COLORS["STATUS_3XX"]
            elif code.startswith("4"):
                color = COLORS["STATUS_4XX"]
            elif code.startswith("5"):
                color = COLORS["STATUS_5XX"]
            else:
                color = COLORS["RESET"]
            return f"{color}{prefix}{code}{suffix}{reset}"

        message = self.STATUS_REGEX.sub(colorize_status, message)
        
        formatted = f"{time_str} | {lvl_str} | {name_str} | {message}"
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
        return formatted


class ProductionFormatter(logging.Formatter):
    """Clean, uncolored structured formatter for Production & Log files"""
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | [%(name)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """
    Configures application logging:
    - In Development: Beautiful color-coded console with clear HTTP status highlights.
    - In Production: Structured machine-readable logs with file rotation.
    - Suppresses noisy 3rd-party library chatter (httpx, transformers, huggingface_hub).
    """
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    if environment.lower() == "development" and sys.stdout.isatty():
        console_handler.setFormatter(ColoredConsoleFormatter())
    else:
        # Fallback or prod
        console_handler.setFormatter(ProductionFormatter())
    root_logger.addHandler(console_handler)
    
    # 2. File Handler (Always structured without ANSI escape codes)
    log_dir = "backend/logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(ProductionFormatter())
    root_logger.addHandler(file_handler)
    
    # 3. Suppress noisy third-party internal loggers unless in DEBUG
    noisy_loggers = [
        "httpx",
        "httpcore",
        "huggingface_hub",
        "transformers",
        "sentence_transformers",
        "urllib3",
        "filelock",
    ]
    for noisy in noisy_loggers:
        logging.getLogger(noisy).setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
