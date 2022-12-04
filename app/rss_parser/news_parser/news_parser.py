"""
Module used for parsing and articles(items) from RSS feed
"""
from typing import Iterable, NoReturn, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import CData


def request_url(url: str) -> str:
    """
    Function requests URL and returns text response if any.
    :param url: URL to request from
    :return: requested URL text
    """
    request = requests.get(url)
    return request.text


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
            return True
    # If attempt to find a link inside description field fails:
    except AttributeError:
        return False
    # In case missed something
    except Exception as exc:
        return False


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
             'rss_header': rss_header,
             'title': item.title.text,
             'description': new_soup.p.text,
             'pubdate': item.pubdate.text if item.pubdate is not None else "Empty",
             'pubdate_format': 'Empty',
             'news_link': item.link.next_sibling.strip(),
             'news_img_link': new_soup.img.get('src') if new_soup.img is not None else "Empty",
             'news_img_location': 'Empty'
        }
        news_list.append(news)
    return news_list


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
            'rss_header': rss_header,
            'title': item.title.text,
            'description': item.description.text if item.description is not None else "Empty",
            'pubdate': item.pubDate.text if item.pubDate is not None else "Empty",
            'pubdate_format': 'Empty',
            'news_link': item.link.text,
            'news_img_link':
                item.find('media:content').get('url') if item.find('media:content') is not None else "Empty",
            'news_img_location': 'Empty'
        }
        news_list.append(news)
    return news_list


def get_rss_header(url: str) -> str:
    soup = BeautifulSoup(request_url(url), 'xml')
    rss_header = soup.channel.title.text
    return rss_header
