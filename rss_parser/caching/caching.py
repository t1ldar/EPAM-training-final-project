"""
Module is used for news caching and handling database queries.
"""
import logging
import os
import sqlite3
from typing import Optional, Iterable

from dateutil import parser

from exceptions.custom_exceptions import NewsNotFoundError
from logs.logger import func_debug_logger

# db file locating
DATABASE_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cached_news.db")

# Module logger setting up
caching_logger = logging.getLogger("app.caching")


class DataBaseHandler(sqlite3.Connection):
    """
    Class for handling operations with sqlite3 database
    """

    __instance = None

    def __init__(self, filename: str) -> None:
        """
        Extending sqlite3.Connection.__init__()
        :param filename: db file location
        """
        super(DataBaseHandler, self).__init__(filename)
        self.__cursor = self.cursor()
        caching_logger.info("DataBaseHandler initialized")

    def __new__(cls, *args, **kwargs):
        """
        Implementing here singleton to have one same connection to db file
        :param args:
        :param kwargs:
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @func_debug_logger(caching_logger)
    def create_table_cached_news(self) -> None:
        """
        Method creating a table called 'cached_news', table name is hardcoded.
        :return: None
        """
        self.execute(
            """CREATE TABLE IF NOT EXISTS cached_news (
                    url text,
                    rss_header text,
                    title text,
                    description text,
                    pubdate text,
                    pubdate_format  text,
                    link text,
                    img_link text,
                    img_location text)"""
        )
        caching_logger.info("'Cached news' table created (if not exists)")

    def drop_table_cached_news(self) -> None:
        """
        Deleting 'cached_news' table method for internal tests
        and for future upgrades if necessary
        :return: None
        """
        self.execute("DROP TABLE IF EXISTS cached_news")
        caching_logger.info("'Cached news' table was dropped")

    @func_debug_logger(caching_logger)
    def read_table_by_pubdate(self, pubdate: int, limit: Optional[int] = False) -> Iterable[dict]:
        """
        Method sending query to db and returning cache news by publication date
        :param pubdate: publication date in YYYYMMDD format
        :param limit: number of news to proceed with
        :return: list of 'cache news' dictionaries with same structure as from 'rss_feed_parser'
        """
        self.row_factory = sqlite3.Row
        self.__cursor = self.cursor()
        self.__cursor.execute(
            "SELECT * FROM cached_news WHERE pubdate_format=:pubdate_format",
            {"pubdate_format": pubdate},
        )
        retrieved_news = [dict(row) for row in self.__cursor.fetchall()]
        if list(retrieved_news):
            caching_logger.info(f"'Found news from {pubdate} in cache")
            if not limit:
                return retrieved_news
            else:
                return retrieved_news[0:limit]
        else:
            caching_logger.error(f"'No news published on {pubdate} in cache found")
            raise NewsNotFoundError(f"No articles published on {pubdate} in cache found")

    @func_debug_logger(caching_logger)
    def read_table_by_pubdate_source(self, pubdate: int, source: str, limit: Optional[int] = False) -> Iterable[dict]:
        """
        Method sending query to db and returning cache news by publication date and source URL
        :param pubdate: publication date in YYYYMMDD format
        :param source: RSS source URL
        :param limit: number of news to proceed with
        :return: list of 'cache news' dictionaries with same structure as from 'rss_feed_parser' func
        """
        self.row_factory = sqlite3.Row
        self.__cursor = self.cursor()
        self.__cursor.execute(
            "SELECT * FROM cached_news WHERE (pubdate_format=:pubdate_format) AND (url=:url)",
            {"pubdate_format": pubdate, "url": source},
        )
        retrieved_news = [dict(row) for row in self.__cursor.fetchall()]
        if list(retrieved_news):
            caching_logger.info(f"'Found news from {source}, {pubdate} in cache")
            if not limit:
                return retrieved_news
            else:
                return retrieved_news[0:limit]
        else:
            caching_logger.error(f"'No news from {source} published in {pubdate} in cache found")
            raise NewsNotFoundError(f"No news from {source} published on {pubdate} in cache found")

    def read_all_table_cached_news(self) -> Iterable[dict]:
        """
        Method returning everything from 'cached_news' table for internal tests
        :return: list of 'cache news' dictionaries
        """
        self.__cursor.execute("SELECT * FROM cached_news")
        return self.__cursor.fetchall()

    @staticmethod
    def format_pubdate(random_date_format: str) -> str:
        """
        Method formatting date to YYYYMMDD
        :param random_date_format: date in random format
        :return: formatted to YYYYMMDD date
        """
        parsed_date = parser.parse(random_date_format)
        formatted_pubdate = parsed_date.strftime("%Y%m%d")
        return formatted_pubdate

    @func_debug_logger(caching_logger)
    def check_news_in_table(self, title: str) -> bool:
        """
        Method checking whether entry with particular 'title' already in database
        :param title: news title
        :return: True if entry exists, False if not
        """
        self.__cursor.execute("SELECT EXISTS (SELECT 1 FROM cached_news WHERE (title=:title))", {"title": title})
        if self.__cursor.fetchone()[0]:
            caching_logger.info(f"Entry with title: '{title}' already exists in the database ")
            return True
        else:
            caching_logger.info(f"Inserting a new entry with title: '{title}' into the database ")
            return False

    @func_debug_logger(caching_logger)
    def insert_into_table_cached_news(self, news_list: Iterable[dict]) -> None:
        """
        Method inserting data into 'cached_news' db
        :param news_list: list of 'cache news' dictionaries with same structure as from 'rss_feed_parser' func
        :return: None
        """
        try:
            for news in news_list:
                # Updating news with additional key 'pubdate_format',
                # formatted date to YYYYMMDD for a further search in database
                pubdate = news["pubdate"]
                if pubdate != "Empty":
                    news["pubdate_format"] = self.format_pubdate(pubdate)
                else:
                    news["pubdate_format"] = "Empty"
                # Check if entry already in table and insert data into a 'cached news' table
                if not self.check_news_in_table(news['title']):
                    self.__cursor.execute(
                        "INSERT INTO cached_news "
                        "VALUES (:url,"
                        " :rss_header,"
                        " :title,"
                        " :description,"
                        " :pubdate,"
                        " :pubdate_format,"
                        " :link,"
                        " :img_link,"
                        " :img_location)",
                        news,
                    )
            caching_logger.info(f"Inserted parsed news into the database")
        except TypeError as exc:
            caching_logger.exception(f"Error occurred during inserting data into db: {exc.__doc__}")
            print(f"Error occurred during inserting data into db: {exc.__doc__}")
