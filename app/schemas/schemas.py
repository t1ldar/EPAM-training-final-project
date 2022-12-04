"""Module defines pydantic schemas for the database"""
from typing import List

import pydantic


class News(pydantic.BaseModel):
    """Class to define News schema """
    id: int
    rss_source: int
    rss_header: str
    title: str
    description: str
    pubdate: str
    pubdate_format: str
    news_link: str
    news_img_link: str
    news_img_location: str

    class Config:
        orm_mode = True


class Rss(pydantic.BaseModel):
    """Class to define Rss source schema"""
    id: int
    rss_url: str
    rss_header: str
    news_list: List[News] = []

    class Config:
        orm_mode = True
