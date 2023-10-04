import logging
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger instance,
    set its level to INFO,
    and configure it to write to a file in the user's home directory.

    Args:
        name: name of the logger
        filesize_mb: maximum size per log file in MB, defaults to 5
        backupcount: number of log files to keep, defaults to 4

    Returns:
        the logger instance
    """
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="{asctime} {filename: <25} {levelname: <8} {message}", style="{")
    formatter.default_time_format = "%Y-%m-%d %H:%M:%S"
    handler = logging.FileHandler(
        filename="logging.log",
        mode="a",
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
