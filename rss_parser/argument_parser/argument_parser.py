import argparse
import logging
from typing import NoReturn

import requests

from exceptions.custom_exceptions import (BlockedRequestError,
                                          NegativeOrZeroLimitArgError,
                                          PageNotFoundError)
from logs.logger import func_debug_logger
from version import version

# Module logger setting up
argument_parser_logger = logging.getLogger('app.argument_parser_module')


def create_arg_parser() -> argparse.Namespace:
    """
    Function parses arguments from CLI and returns them
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Pure Python command-line RSS reader.")
    parser.add_argument("source", nargs="?", default=False, help="RSS URL")
    parser.add_argument("--version", action="version", version=f"Version {version}", help="Print version info")
    parser.add_argument("--json", action="store_true", help="Print result as JSON in stdout")
    parser.add_argument("--verbose", action="store_false", help="Outputs verbose status messages")
    parser.add_argument("--limit", action="store", default=False, help="Limit news topics if this parameter provided")
    parser.add_argument("--date", action="store", default=False, help="Get news from cache, use date format: YYYYMMDD")
    parser.add_argument("--to-html",
                        action="store",
                        default=False,
                        dest='path_html',
                        help="""
                        Convert news into HTML file.
                        Indicate path (for win OS examples 'c:\\temp', 'c:\\temp\\ex.pdf'),
                        for Ubuntu examples './' or '~/Documents'), filename is optional.
                        """
                        )
    parser.add_argument("--to-pdf",
                        action="store",
                        default=False,
                        dest='path_pdf',
                        help="Convert news into PDF file. Indicate path, filename is optional")
    parser.add_argument("--to-epub",
                        action="store",
                        default=False,
                        dest='path_epub',
                        help="Convert news into EPUB file. Indicate path, filename is optional")
    parser.add_argument("--colorize", action="store_true", help="Output colorization")
    args = parser.parse_args()
    return args


@func_debug_logger(argument_parser_logger)
def validate_limit_arg(value: int) -> int:
    """
    Function validates limit argument from args_parser,
    returns original value if ok. Raises exceptions if value is wrong
    :return: args.limit value if it is valid
    :raise: NonIntegerLimitArgError if value is not an integer
    :raise: NegativeOrZeroLimitArgError if value <=0
    """
    try:
        value = int(value)
    except ValueError:
        argument_parser_logger.exception(f"Limit argument is not an integer({value})", exc_info=False)
        raise
    if value <= 0:
        argument_parser_logger.exception(f"Not valid limit argument ({value})", exc_info=False)
        raise NegativeOrZeroLimitArgError
    else:
        argument_parser_logger.info(f"Limit argument is valid and equals {value}")
        return value


@func_debug_logger(argument_parser_logger)
def validate_source(url: str) -> NoReturn:
    """
    Function requests source and raises multiple exceptions if
    something wrong with a source.
    :param url: source URL
    :return: None
    :raises: raises multiple exceptions if URL is not valid or not available
    """
    try:
        request = requests.get(url)
        if request.status_code == 404:
            argument_parser_logger.error(f"Page {url} is not found")
            raise PageNotFoundError
        elif request.status_code == 403:
            argument_parser_logger.error(f"Request to {url} was blocked on a server side")
            raise BlockedRequestError
    # Raise multiple exceptions if link is somehow broken
    except Exception:
        raise
    else:
        argument_parser_logger.info(f"Source '{url}' is valid")


@func_debug_logger(argument_parser_logger)
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
        argument_parser_logger.error("No internet connection")
        raise
    else:
        argument_parser_logger.info(f"Connection to internet exists")
