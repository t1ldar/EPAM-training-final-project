"""Module used for error handling"""


class NotRssFeedUrlError(Exception):
    """Error raised if url doesn't lead to RSS feed"""
    pass


class NewsNotFound(Exception):
    """Error raised if url doesn't lead to RSS feed"""
    pass


class NotValidLimitArg(Exception):
    """Error raised if url doesn't lead to RSS feed"""
    pass


class NotValidFilename(Exception):
    """Error raised if input filename is not valid"""
    pass
