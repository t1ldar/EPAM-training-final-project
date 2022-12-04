"""
Module for custom exceptions
"""


class Error(Exception):
    """General error passes the message"""
    pass


class NegativeOrZeroLimitArgError(Exception):
    """Error is raised then value is <= 0"""
    pass


class NotRssFeedUrlError(Exception):
    """Error raised if url doesn't lead to RSS feed"""
    pass


class PageNotFoundError(Exception):
    """Error is raised then page is not found. Response -404"""
    pass


class BlockedRequestError(Exception):
    """Error is raised then request is blocked on a server side"""
    pass


class NoInternetConnection(Exception):
    """Error is raised then there is noe internet connection"""
    pass


class NewsNotFoundError(Exception):
    """Error is raised then news are not found in a database"""
    pass


class WrongPathError(Exception):
    """Error is raised then specified path is not found"""
    pass
