"""
Debug Logger System - Centralized logging för hela applikationen
Varje modul använder denna för full debug tracking
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class DebugLogger:
    """Centralized debug logging system"""
    
    _instance: Optional['DebugLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern för global logger"""
        if cls._instance is None:
            print(f"[DEBUG_LOGGER] Creating new DebugLogger instance at {datetime.now()}")
            cls._instance = super(DebugLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger om inte redan gjort"""
        if not DebugLogger._initialized:
            print(f"[DEBUG_LOGGER] Initializing logger system at {datetime.now()}")
            self._setup_logger()
            DebugLogger._initialized = True
            self.info("DebugLogger", "Logger system initialized successfully")
    
    def _setup_logger(self):
        """Setup logging configuration"""
        print(f"[DEBUG_LOGGER] Setting up logger configuration")
        
        # Skapa logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        print(f"[DEBUG_LOGGER] Log directory created/verified: {log_dir.absolute()}")
        
        # Skapa log fil med timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"multiteam_{timestamp}.log"
        print(f"[DEBUG_LOGGER] Log file path: {log_file.absolute()}")
        
        # Configure root logger
        self.logger = logging.getLogger("MultiTeam")
        self.logger.setLevel(logging.DEBUG)
        print(f"[DEBUG_LOGGER] Logger level set to DEBUG")
        
        # File handler - allt loggas till fil
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        print(f"[DEBUG_LOGGER] File handler added: {log_file}")
        
        # Console handler - endast INFO och högre till console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)-8s | %(name)-15s | %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        print(f"[DEBUG_LOGGER] Console handler added")
        
        self.logger.propagate = False
        print(f"[DEBUG_LOGGER] Logger setup completed")
    
    def debug(self, module: str, message: str, **kwargs):
        """Log debug message"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.debug(f"[{module}] {message}{extra_info}")
    
    def info(self, module: str, message: str, **kwargs):
        """Log info message"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.info(f"[{module}] {message}{extra_info}")
    
    def warning(self, module: str, message: str, **kwargs):
        """Log warning message"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.warning(f"[{module}] {message}{extra_info}")
    
    def error(self, module: str, message: str, **kwargs):
        """Log error message"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.error(f"[{module}] {message}{extra_info}")
    
    def critical(self, module: str, message: str, **kwargs):
        """Log critical message"""
        extra_info = f" | {kwargs}" if kwargs else ""
        self.logger.critical(f"[{module}] {message}{extra_info}")
    
    def exception(self, module: str, message: str, exc_info=True):
        """Log exception with traceback"""
        self.logger.exception(f"[{module}] {message}", exc_info=exc_info)


# Global logger instance
logger = DebugLogger()

# Convenience functions för enkel import
def debug(module: str, message: str, **kwargs):
    """Global debug function"""
    logger.debug(module, message, **kwargs)

def info(module: str, message: str, **kwargs):
    """Global info function"""
    logger.info(module, message, **kwargs)

def warning(module: str, message: str, **kwargs):
    """Global warning function"""
    logger.warning(module, message, **kwargs)

def error(module: str, message: str, **kwargs):
    """Global error function"""
    logger.error(module, message, **kwargs)

def critical(module: str, message: str, **kwargs):
    """Global critical function"""
    logger.critical(module, message, **kwargs)

def exception(module: str, message: str):
    """Global exception function"""
    logger.exception(module, message)


if __name__ == "__main__":
    # Test logger
    print("Testing DebugLogger...")
    debug("TEST", "This is a debug message")
    info("TEST", "This is an info message")
    warning("TEST", "This is a warning message")
    error("TEST", "This is an error message")
    critical("TEST", "This is a critical message")
    print("Logger test completed. Check logs directory.")
