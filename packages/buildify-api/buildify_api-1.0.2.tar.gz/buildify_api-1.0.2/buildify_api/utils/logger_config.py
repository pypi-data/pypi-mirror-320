import logging
import os
from pathlib import Path

# Directory for logs
LOG_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'logs')


def get_logger(name: str, log_to_file: bool = True) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name (str): Name of the logger.
        log_to_file (bool): If True, logs will be saved to a file (only if writable). Defaults to True.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if the logger is already configured
    if not logger.hasHandlers():
        # Handlers
        stream_handler = logging.StreamHandler()
        handlers = [stream_handler]

        # File handler (optional, if enabled and writable)
        if log_to_file:
            try:
                os.makedirs(LOG_DIR, exist_ok=True)
                log_file = os.path.join(LOG_DIR, f'{name}.log')
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                handlers.append(file_handler)
            except OSError as e:
                # If the file system is read-only, log to console only
                logging.warning(f"File logging disabled due to error: {e}")

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Apply formatter to all handlers
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Set log level
        logger.setLevel(logging.INFO)

    return logger
