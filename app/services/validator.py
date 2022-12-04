"""Module combines various validator functions"""
from typing import NoReturn, Optional

import requests
from bs4 import BeautifulSoup

from errors import exception_handler


def validate_limit_arg(value: int) -> int:
    """
    Validate limit argument
    :param value: input value
    :return: same value if no exception raised
    """
    try:
        value = int(value)
    except ValueError:
        raise exception_handler.NotValidLimitArg
    if value <= 0:
        raise exception_handler.NotValidLimitArg
    else:
        return value


def validate_url_is_rss_feed(url: str) -> None:
    """
    Validate url if it is a valid rss source
    :param url: url
    :return: None, raises if url doesn't lead to rss feed
    """
    try:
        request = requests.get(url)
    except Exception:
        raise
    soup = BeautifulSoup(request.text, 'xml')
    text = soup.find_all('rss')
    if not text:
        raise exception_handler.NotRssFeedUrlError


def validate_filename(filename: Optional[str]) -> None:
    """Validate if filename was passed in the Form"""
    if filename is None:
        raise exception_handler.NotValidFilename


def check_internet_connection() -> NoReturn:
    """
    Checks internet connection via accessing www.google.com web-site.
    Maybe there is a better solution, didn't find any better.
    :return: None
    :raise requests.exceptions.ConnectionError: if no connection to internet
    """
    try:
        request = requests.get("https://www.google.com/")
    except requests.exceptions.ConnectionError:
        raise
