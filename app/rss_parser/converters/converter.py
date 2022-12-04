"""
Module is used for converting news into html format
"""
import json
import os
import uuid
from typing import Iterable, Optional

import jinja2.exceptions
from ebooklib import epub
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa


class Converter:
    """
    Converter class handling conversions into different formats
    """

    TEMPLATES_LOCATION: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

    @staticmethod
    def convert_to_json(news_list: Iterable[dict]) -> str:
        """
        Method converts parsed news from RSS feed into json
        :param news_list: parsed list of news
        :return: json data
        """
        news_list_array = []
        for news in news_list:
            news_list_modified = {
                "Feed": news['rss_header'],
                "URL": news['url'],
                "Article": {
                    'title': news['title'],
                    'pubdate': news['pubdate'],
                    'description': news['description'],
                    'link': news['news_link'],
                    'img_link': news['news_img_link']
                }
            }
            news_list_array.append(news_list_modified)
        json_dumped = json.dumps(news_list_array, indent=4, ensure_ascii=False)
        return json_dumped

    @staticmethod
    def setup_jinja(template_filename: str) -> jinja2.Template:
        """
        Setting up jinja with a given template
        :param template_filename: html template file name in templates folder
        :return: template jinja object
        """
        jinja_env = Environment(loader=FileSystemLoader(Converter.TEMPLATES_LOCATION))
        jinja_html_template = jinja_env.get_template(template_filename)

        return jinja_html_template

    @classmethod
    def convert_to_html(cls, target_path: str, news_list: Iterable[dict]) -> None:
        """
        Method converting RSS feed into HTML file and saves into specified location
        :param target_path: path there to save html file
        :param news_list: parsed news feed
        :return: None
        """
        if not os.path.join(target_path).endswith('.html'):
            html_file_name = f"rss_feed_{str(uuid.uuid4())[0:6]}.html"
            target_path = os.path.join(target_path, html_file_name)
        try:
            template = cls.setup_jinja('html_template.html')
            with open(target_path, 'w+', encoding='utf-8') as file:
                file.write(template.render(news_list=news_list))
        except TypeError:
            print("Not valid path or input data.")
        except AttributeError:
            print("HTML rendering with jinja failed, template not found or input data is wrong")
        except jinja2.exceptions.TemplateNotFound:
            print("HTML template not found.")
        except FileNotFoundError:
            raise

    @classmethod
    def convert_to_pdf(cls, target_path: str, news_list: Iterable[dict]) -> None:
        """
        Method converting RSS feed into PDF file and saves into specified location
        :param target_path: path there to save html file
        :param news_list: parsed news feed
        :return: None
        """
        if not os.path.join(target_path).endswith('.pdf'):
            pdf_file_name = f"rss_feed_{str(uuid.uuid4())[0:6]}.pdf"
            target_path = os.path.join(target_path, pdf_file_name)
        try:
            template = cls.setup_jinja('html_template.html')
            source_html_text = template.render(news_list=news_list)
            with open(target_path, "w+b") as target:
                pisa.CreatePDF(source_html_text, dest=target)
        except FileNotFoundError:
            raise
        except Exception as exc:
            print(exc)

    @classmethod
    def convert_to_epub(cls, target_path: str, news_list: Iterable[dict]) -> None:
        if not os.path.join(target_path).endswith('.epub'):
            epub_file_name = f"rss_feed_{str(uuid.uuid4())[0:6]}.epub"
            target_path = os.path.join(target_path, epub_file_name)
        try:
            # Setting up an ebook
            book = epub.EpubBook()
            book.set_identifier('id0001')
            book.set_title('RSS feed book content:')
            book.set_language('en')
            book.add_author('RSS-parser')
            # Setting a book cover image
            book_cover_image = os.path.join(Converter.TEMPLATES_LOCATION, 'epub_book_cover.jpg')
            with open(book_cover_image, 'rb') as image:
                cover_image_file = image.read()
            book.set_cover('image.jpg', cover_image_file)
            # Setting book structure
            book.spine = ['cover', 'nav']
            # Table of contents
            toc = []
            for page_number, news in enumerate(news_list):
                template = cls.setup_jinja('epub_template.html')
                source_html_text = template.render(news=news, page_number=page_number)
                # Adding page to a book via html template
                book_page = epub.EpubHtml(
                    title=news['title'],
                    file_name=f"book_page_{page_number}.xhtml",
                    lang='en'
                )
                book_page.content = source_html_text
                book.add_item(book_page)
                if news['news_img_location'] != 'Empty':
                    with open(news['news_img_location'], 'rb') as image:
                        page_image_file = image.read()
                else:
                    # Could be done using different template
                    with open(os.path.join(Converter.TEMPLATES_LOCATION, 'epub_empty_image.jpg'), 'rb') as image:
                        page_image_file = image.read()
                page_image = epub.EpubItem(
                    uid=f"image{page_number}",
                    file_name=f"image{page_number}",
                    content=page_image_file
                )
                book.add_item(page_image)
                # Updating book with a page
                book.spine.append(book_page)
                # Updating table of contents
                toc.append(epub.Section(news['title']))
                toc.append(book_page)

            book.toc = tuple(toc)
            # Setting book navigation
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            # Zipping into a book
            epub.write_epub(target_path, book, {})
        except FileNotFoundError:
            raise
        except Exception as exc:
            print(exc)
