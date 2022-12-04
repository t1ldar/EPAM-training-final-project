"""
Module used for parsing and articles(items) from RSS feed
"""
import logging
from textwrap import TextWrapper
from typing import Iterable, NoReturn, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import CData
from colors import color

from exceptions.custom_exceptions import NotRssFeedUrlError
from logs.logger import func_debug_logger

# Module logger setting up
news_parser_logger = logging.getLogger('app.news_parser_module')


def request_url(url: str) -> str:
    """
    Function requests URL and returns text response if any.
    :param url: URL to request from
    :return: requested URL text
    """
    request = requests.get(url)
    return request.text


@func_debug_logger(news_parser_logger)
def validate_url_is_rss_feed(url: str) -> NoReturn:
    """
    Checks the link whether is it leading to RSS feed or not
    :param url: URL to validate
    :return: None
    :raise NotRssFeedUrlError: if URL is not an RSS feed
    """
    soup = BeautifulSoup(request_url(url), 'xml')
    text = soup.find_all('rss')
    if not text:
        news_parser_logger.error(f"URL '{url}' doesn't lead to RSS feed")
        raise NotRssFeedUrlError
    news_parser_logger.info(f"URL '{url}' is valid RSS feed")


@func_debug_logger(news_parser_logger)
def rss_feed_type_checker(url: str) -> bool:
    """
    Trying to separate RSS feeds with CDATA in description field
    with image links inside (mixed xml) and RSS feeds with plain description.
    In the first case we will use "html.parser", in the second case 'lxml' parser.
    Unfortunately, I haven't found any 'good enough' method to separate them, except this
    solution via BeautifulSoup error raising
    :param url: URL to RSS feed
    :return: True if RSS feed contains nonXML data, False if plain xml
    """
    try:
        # Attempt to parse non-XMl data
        soup = BeautifulSoup(request_url(url), 'html.parser')
        description_soup = BeautifulSoup(
            soup.find('item').find('description').find(text=lambda x: isinstance(x, CData)), 'html.parser'
        )
        # img_link = soup_test_2.find('img').get('src')
        link_inside = description_soup.find('a')
        if link_inside:
            news_parser_logger.info("RSS feed description field contains non-XML data")
            return True
    # If attempt to find a link inside description field fails:
    except AttributeError:
        news_parser_logger.info(f"Regular RSS feed found")
        return False
    # In case missed something
    except Exception as exc:
        news_parser_logger.info(f"Exception from 'rss_feed_type_checker' func: {exc}")
        return False


@func_debug_logger(news_parser_logger)
def parse_rss_feed_with_non_xml(url: str, limit_arg: Optional[int] = None) -> Iterable[dict]:
    """
    Function parses rss feed and returns list of news.
    Parser used for RSS feed with CDATA under description tag
    :param url: URL to RSS feed
    :param limit_arg: number of news to return in a list
    :return: list of news as dictionaries
    """
    soup = BeautifulSoup(request_url(url), 'html.parser')
    # Looking for the top rss header title
    rss_header = soup.channel.title.text
    # Selecting all items of RSS feed with limit argument
    rss_news_limited = soup.find_all('item', limit=limit_arg)
    news_list = []
    for item in rss_news_limited:
        # Generating new soup for second parsing iteration under description tag
        new_soup = BeautifulSoup(item.find('description').find(text=lambda x: isinstance(x, CData)),
                                 'html.parser')
        news = {
             'url': url,
             'rss_header': rss_header,
             'title': item.title.text,
             'description': new_soup.p.text,
             'pubdate': item.pubdate.text if item.pubdate is not None else "Empty",
             'pubdate_format': 'Empty',
             'link': item.link.next_sibling.strip(),
             'img_link': new_soup.img.get('src') if new_soup.img is not None else "Empty",
             'img_location': 'Empty'
        }
        news_list.append(news)
    news_parser_logger.info(f"News successfully parsed from {url}")
    return news_list


@func_debug_logger(news_parser_logger)
def parse_rss_feed_regularly(url: str, limit_arg: Optional[int] = None) -> Iterable[dict]:
    """
    Function parses rss feed and returns list of news.
    Parser used for regular xml RSS feed.
    :param url: URL to RSS feed
    :param limit_arg: number of news to return in a list
    :return: list of news as dictionaries
    """
    soup = BeautifulSoup(request_url(url), 'xml')
    # Looking for the top rss header
    rss_header = soup.channel.title.text
    # Selecting all items of RSS feed
    rss_news_limited = soup.find_all('item', limit=limit_arg)
    news_list = []
    for item in rss_news_limited:
        news = {
            'url': url,
            'rss_header': rss_header,
            'title': item.title.text,
            'description': item.description.text if item.description is not None else "Empty",
            'pubdate': item.pubDate.text if item.pubDate is not None else "Empty",
            'pubdate_format': 'Empty',
            'link': item.link.text,
            'img_link': item.find('media:content').get('url') if item.find('media:content') is not None else "Empty",
            'img_location': 'Empty'
        }
        news_list.append(news)
    news_parser_logger.info(f"News successfully parsed from {url}")
    return news_list


def pretty_print_out(news_list: Iterable[dict], colorize: Optional[bool] = False) -> None:
    """
    Prints out news RSS feed in human-readable format
    :param colorize: bool, True if colorize output to stdout
    :param news_list: list of RSS item as dictionary
    :return: None, just prints out items or exception message
    """
    wrap_text_box = TextWrapper(width=110)
    if news_list:
        news_parser_logger.info("Printing out articles:")
        print(color(f"Feed: {news_list[0]['rss_header']}", bg='yellow' if colorize else 0))
        print()
        for news in news_list:
            print(
                color(f"Title: {news['title']}", bg='blue' if colorize else 0) + '\n' +
                color(f"Date: {news['pubdate']}", bg='red' if colorize else 0) + '\n' + '\n' +
                color(f"Description:", fg='white' if colorize else 0, style='bold' if colorize else 0)
            )
            for description in wrap_text_box.wrap(news['description']):
                print(color(description, fg='cyan' if colorize else 0, style='bold' if colorize else 0))
            print()
            print(
                color(f"Links:", fg='magenta' if colorize else 0, style='bold' if colorize else 0) + '\n' +
                color(f"[1]: {news['link']}", fg='green' if colorize else 0)
            )
            if news['img_link'] != "Empty":
                print(color(f"[2]: {news['img_link']}", fg='green' if colorize else 0))
            print("----------------------------------")
