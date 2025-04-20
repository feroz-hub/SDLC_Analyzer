import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir: str, log_file: str = "semantic_api.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging with file and console handlers.

    Args:
        log_dir (str): Directory for log files.
        log_file (str): Name of the log file (default: semantic_api.log).
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.

    Raises:
        OSError: If log directory creation or file access fails.
    """
    logger = logging.getLogger()  # Get root logger to ensure all modules inherit handlers
    if logger.hasHandlers():
        logger.handlers.clear()  # Clear existing handlers to avoid duplicates

    try:
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)

        # Verify write permissions
        if not os.access(log_dir, os.W_OK):
            raise OSError(f"No write permission for log directory: {log_dir}")

        # Configure handlers
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        console_handler = logging.StreamHandler()

        # Set format
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(level)

        # Test logging
        logger.info(f"Logging initialized to {log_path}")
        logger.debug(f"Log directory: {log_dir}, Log file: {log_path}")

        return logger
    except Exception as e:
        print(f"Failed to configure logging: {str(e)}")
        raise

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name (str): Name of the logger (usually __name__).

    Returns:
        logging.Logger: Logger instance.
    """
    return logging.getLogger(name)