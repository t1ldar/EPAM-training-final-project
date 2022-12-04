"""
Module is used for image caching from parsed image links
"""
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, NoReturn

import requests
from PIL import Image


class ImageHandler:
    """
        Class for handling operations with image caching and image processing
    """

    CACHED_IMAGES_LOCATION: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cached_images')

    def __init__(self, news_list: Iterable[dict]) -> None:
        """
        ImageHandler class initializing with news_list
        :param news_list: list of dicts of parsed news
        """
        self.news_list = news_list

    @staticmethod
    def download_image(news: dict) -> None:
        """
        Function is used for downloading an image
        and updating news dictionary with cached image file
        location value
        :param news: parsed news in dictionary format
        :return: None
        """
        # Setting a unique filename for each news title, not to download them every time.
        filename_generator = f"img_{str(news['title'][0:15]).lower().replace(' ', '')}.png"
        cache_img_location = os.path.join(ImageHandler.CACHED_IMAGES_LOCATION, filename_generator)
        # If cached image doesn't exist - download it
        if not os.path.isfile(cache_img_location):
            if news['news_img_link'] != 'Empty':
                url_request = requests.get(news['news_img_link'])
                with open(cache_img_location, 'wb') as file:
                    file.write(url_request.content)
                news['news_img_location'] = cache_img_location
            else:
                news['news_img_location'] = 'Empty'
        else:
            news['news_img_location'] = cache_img_location

    @staticmethod
    def resize_image(image_location: str) -> None:
        """
        Function is used for an image resizing for
        further correct placement into html template

        :param image_location: local cache image location
        :return:None
        """
        if image_location != 'Empty':
            # Setting up max width for HTML template
            image_width_for_html = 250
            image = Image.open(image_location)
            if image.size[0] > 250:
                # Calculating image size ration
                width_percent = (image_width_for_html / float(image.size[0]))
                height_size = int((float(image.size[1]) * float(width_percent)))
                # Resize and save with same filename
                img = image.resize((image_width_for_html, height_size), Image.LANCZOS)
                img.save(image_location)

    def download_images_concurrently(self) -> NoReturn:
        """
        Function used as a wrapper for multithreaded
        downloading of images

        :return: None
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.download_image, self.news_list)

    def resize_cached_images_concurrently(self) -> NoReturn:
        """
        Function used as a wrapper for multithreaded
        resizing of images

        :return: None
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.resize_image, [news['news_img_location'] for news in self.news_list])
