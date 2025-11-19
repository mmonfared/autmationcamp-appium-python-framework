"""
Logging configuration for mobile testing framework
Provides structured logging with file and console output
"""

import os
import logging
import logging.config
from datetime import datetime
import yaml
import colorlog


def setup_logging(config_path: str = None):
    """
    Setup logging configuration

    Args:
        config_path: Path to logging configuration file
    """
    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/test_execution_{timestamp}.log"

    # Default logging configuration
    default_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'console': {
                'format': '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
                'datefmt': '%H:%M:%S',
                '()': colorlog.ColoredFormatter,
                'log_colors': {
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': log_filename,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'console',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # Root logger
                'level': 'DEBUG',
                'handlers': ['file', 'console'],
                'propagate': True
            },
            'urllib3': {
                'level': 'WARNING',
                'handlers': ['file'],
                'propagate': False
            },
            'selenium': {
                'level': 'WARNING',
                'handlers': ['file'],
                'propagate': False
            }
        }
    }

    # Load custom configuration if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load logging config from {config_path}: {e}")
            config = default_config
    else:
        config = default_config

    # Apply configuration
    logging.config.dictConfig(config)

    # Log setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup completed. Log file: {log_filename}")


class TestLogger:
    """
    Enhanced logger for test cases with additional functionality
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.test_start_time = None
        self.step_count = 0

    def start_test(self, test_name: str):
        """Mark the start of a test"""
        self.test_start_time = datetime.now()
        self.step_count = 0
        self.logger.info(f"🚀 Starting test: {test_name}")
        self.logger.info(f"Test started at: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def end_test(self, test_name: str, status: str = "COMPLETED"):
        """Mark the end of a test"""
        if self.test_start_time:
            end_time = datetime.now()
            duration = (end_time - self.test_start_time).total_seconds()
            self.logger.info(f"🏁 Test {status}: {test_name}")
            self.logger.info(f"Test duration: {duration:.2f} seconds")
            self.logger.info(f"Total steps executed: {self.step_count}")
        else:
            self.logger.info(f"🏁 Test {status}: {test_name}")

    def step(self, step_description: str):
        """Log a test step"""
        self.step_count += 1
        self.logger.info(f"📋 Step {self.step_count}: {step_description}")

    def action(self, action_description: str):
        """Log a test action"""
        self.logger.info(f"⚡ Action: {action_description}")

    def verification(self, verification_description: str, result: bool):
        """Log a verification step"""
        status = "✅ PASS" if result else "❌ FAIL"
        self.logger.info(f"🔍 Verification: {verification_description} - {status}")

    def screenshot(self, screenshot_path: str):
        """Log screenshot capture"""
        self.logger.info(f"📸 Screenshot captured: {screenshot_path}")

    def error(self, error_message: str):
        """Log an error"""
        self.logger.error(f"🚨 ERROR: {error_message}")

    def warning(self, warning_message: str):
        """Log a warning"""
        self.logger.warning(f"⚠️  WARNING: {warning_message}")

    def debug(self, debug_message: str):
        """Log debug information"""
        self.logger.debug(f"🐛 DEBUG: {debug_message}")

    def info(self, info_message: str):
        """Log general information"""
        self.logger.info(f"ℹ️  INFO: {info_message}")

    def performance(self, operation: str, duration: float):
        """Log performance metrics"""
        self.logger.info(f"⏱️  PERFORMANCE: {operation} took {duration:.2f} seconds")


def get_test_logger(name: str) -> TestLogger:
    """
    Get a test logger instance

    Args:
        name: Logger name (usually test class or method name)

    Returns:
        TestLogger instance
    """
    return TestLogger(name)
