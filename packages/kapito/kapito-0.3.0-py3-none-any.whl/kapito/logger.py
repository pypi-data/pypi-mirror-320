import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with rich formatting.

    Args:
        name (str): The name of the logger (usually __name__).
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: A configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        # Create a rich handler
        rich_handler = RichHandler(
            show_time=True,
            show_level=True,
            show_path=True,
        )
        logger.addHandler(rich_handler)

    return logger
