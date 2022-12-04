"""Module declares sqlalchemy models"""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Rss(Base):
    """
    Class to define rss source model
    """
    __tablename__ = "rss_book"
    id = Column(Integer, primary_key=True, index=True)
    rss_url = Column(String)
    rss_header = Column(String)

    news_list = relationship("News", back_populates="rss", cascade="all, delete-orphan")


class News(Base):
    """
    Class to define News model
    """
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    rss_source = Column(Integer, ForeignKey("rss_book.id"))
    rss_header = Column(String)
    title = Column(String)
    description = Column(String)
    pubdate = Column(String)
    pubdate_format = Column(String)
    news_link = Column(String)
    news_img_link = Column(String)
    news_img_location = Column(String)

    rss = relationship("Rss", back_populates='news_list')
