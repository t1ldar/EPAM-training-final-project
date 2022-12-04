"""
Module is used for setting up a logger
"""
import logging
from functools import wraps
from typing import Any, Callable, Optional

from colorlog import ColoredFormatter


def setup_app_logger(colored: Optional[bool] = False, disabled: Optional[bool] = True) -> logging.Logger:
    """
    Application logging feature setting up
    :return: logger object
    """
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG)
    # Setting up an StreamHandler and Formatter
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s: %(message)s")
    if colored:
        formatter = ColoredFormatter(
            "%(red)s%(asctime)s %(bold_white)s|"
            " %(log_color)s%(levelname)s %(white)s|"
            "%(thin_yellow)s %(name)s: %(log_color)s%(message)s",
            log_colors={
                'DEBUG': 'bold_blue',
                'INFO': 'bold_green',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'red,bg_white'
            }
        )
    stream_handler.setFormatter(formatter)
    app_logger.addHandler(stream_handler)
    if disabled:
        logging.disable()
    return app_logger


def func_debug_logger(logger: logging.Logger) -> Callable[..., Any]:
    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Simple logger decorator, logging start/end of a function
        :param func: func to decorate
        :return: None
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"'{func.__name__}' func called")
            result = func(*args, **kwargs)
            logger.debug(f"'{func.__name__}' func exits")
            return result
        return wrapper
    return inner
