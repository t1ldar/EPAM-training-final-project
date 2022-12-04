"""
Module used for parsing arguments from CLI and as entry point of a program
"""
import os
import sys

import requests

from argument_parser.argument_parser import (check_internet_connection,
                                             create_arg_parser,
                                             validate_limit_arg,
                                             validate_source)
from caching.caching import DATABASE_FILE, DataBaseHandler
from caching.caching_images import ImageHandler
from converters.converter import Converter
from exceptions import custom_exceptions
from logs.logger import setup_app_logger
from news_parser.news_parser import (parse_rss_feed_regularly,
                                     parse_rss_feed_with_non_xml,
                                     pretty_print_out, rss_feed_type_checker,
                                     validate_url_is_rss_feed)


def main() -> None:
    """
    Entry point to RSS reader
    :return:
    """
    args = create_arg_parser()

    # Setting up logger
    logger = setup_app_logger(
        colored=args.colorize,
        disabled=args.verbose
    )

    # Validate limit argument if given on start. Exit if something is wrong
    if args.limit:
        try:
            validate_limit_arg(args.limit)
        except ValueError:
            sys.exit(f"Error. Limit argument '{args.limit}' is not an integer. Please enter a positive integer")
        except custom_exceptions.NegativeOrZeroLimitArgError:
            sys.exit(f"Error. Limit argument '{args.limit}' is negative or zero. Please enter a positive integer")
        else:
            # Setting limit argument to an integer
            args.limit = int(args.limit)

    # Check internet connection. Decided to do separately, due to
    # some interference with further validators and requests.exceptions.ConnectionError
    if not args.date:
        try:
            check_internet_connection()
        except requests.exceptions.ConnectionError:
            sys.exit("No internet connection. Pass 'date' argument to get news from local cache")

    # Validate URL and if it is leading to RSS feed
    if not args.date:
        try:
            validate_source(args.source)
            validate_url_is_rss_feed(args.source)
        except custom_exceptions.NotRssFeedUrlError:
            sys.exit(f"Error. URL source '{args.source}' doesn't lead to RSS feed")
        except custom_exceptions.BlockedRequestError:
            sys.exit(f"{args.source} blocked request on a server side")
        except custom_exceptions.PageNotFoundError:
            sys.exit(f"Page {args.source} not found")
        # Broken links will raise multiple errors in 'validate source' func
        # which are caught here
        except Exception as exc:
            sys.exit(f"Link is broken or source is missing. Check error:{exc.__doc__}")

    # Creating db file if it doesn't exist
    if not os.path.isfile(DATABASE_FILE):
        with DataBaseHandler(DATABASE_FILE) as db:
            db.create_table_cached_news()

    # If args.date is not parsed get news from internet and insert them into the database
    if not args.date:
        # Check the type of RSS feed
        rss_type = rss_feed_type_checker(args.source)
        if rss_type:
            news_list = parse_rss_feed_with_non_xml(
                url=args.source,
                limit_arg=args.limit
            )
        else:
            news_list = parse_rss_feed_regularly(
                url=args.source,
                limit_arg=args.limit
            )
        # Cache images from parsed news for further offline news format converters
        cache_images = ImageHandler(news_list)
        cache_images.download_images_concurrently()
        cache_images.resize_cached_images_concurrently()
        # Insert parsed news into a database
        with DataBaseHandler(DATABASE_FILE) as db:
            db.insert_into_table_cached_news(news_list)

    # If args.date parsed from CLI, get news from cache
    if args.date:
        try:
            if not args.source:
                with DataBaseHandler(DATABASE_FILE) as db:
                    news_list = db.read_table_by_pubdate(
                        pubdate=args.date,
                        limit=args.limit)
            else:
                with DataBaseHandler(DATABASE_FILE) as db:
                    news_list = db.read_table_by_pubdate_source(
                        pubdate=args.date,
                        source=args.source,
                        limit=args.limit)
        except custom_exceptions.NewsNotFoundError as exc:
            sys.exit(exc)

    # Convert to HTML
    if args.path_html:
        try:
            Converter.convert_to_html(args.path_html, news_list)
        except FileNotFoundError:
            sys.exit(f"Specified path/folder {args.path_epub} doesn't exist.")

    # Convert to PDF
    if args.path_pdf:
        try:
            Converter.convert_to_pdf(args.path_pdf, news_list)
        except FileNotFoundError:
            sys.exit(f"Specified path/folder {args.path_epub} doesn't exist.")

    # Convert to EPUB
    if args.path_epub:
        try:
            Converter.convert_to_epub(args.path_epub, news_list)
        except FileNotFoundError:
            sys.exit(f"Specified path/folder {args.path_epub} doesn't exist.")

    # Convert to JSON or pretty print
    if args.json:
        print(Converter.convert_to_json(news_list, args.colorize))
    else:
        pretty_print_out(news_list, args.colorize)


if __name__ == "__main__":
    main()
