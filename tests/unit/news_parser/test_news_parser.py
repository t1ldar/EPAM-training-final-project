import pytest

from rss_parser.news_parser.news_parser import (NotRssFeedUrlError,
                                                rss_feed_type_checker,
                                                validate_url_is_rss_feed, parse_rss_feed_regularly)


@pytest.mark.parametrize('expected_exception, url', [(NotRssFeedUrlError, 'http://www.google.com')])
def test_validate_url_is_rss_feed(expected_exception, url):
    with pytest.raises(expected_exception):
        validate_url_is_rss_feed(url)


@pytest.mark.parametrize('url, expected_result', [('https://lifehacker.com/rss', True),
                                                  ('https://news.yahoo.com/rss', False),
                                                  ('https://rss.dw.com/xml/rss-ru-ger', False)])
def test_rss_feed_type_checker(url, expected_result):
    assert rss_feed_type_checker(url) == expected_result
