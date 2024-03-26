import logging
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger instance,
    set its level to INFO,
    and configure it to write to a file in the user's home directory.

    Args:
        name: name of the logger (usually __name__ of the calling module)

    Returns:
        a logger instance
    """
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)
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


def log_start_of_script(logger: logging.Logger, host: str, shortcode: str) -> None:
    """
    Make a log entry to make it clear that a new run begins.
    """
    msg = f"Start script for project {shortcode} on server {host}"
    logger.info("")
    logger.info("*" * len(msg))
    logger.info("DSP-PERMISSIONS-SCRIPTS")
    logger.info(msg)
    logger.info("*" * len(msg))
    logger.info("")

    print(f"\n{msg}")
    logfile = [handler.baseFilename for handler in logger.handlers if isinstance(handler, logging.FileHandler)][0]
    print(f"There will be no print output, only logging to file {logfile}")
