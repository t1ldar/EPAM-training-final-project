"""Module provides CRUD operations with database"""
from typing import Any, Optional

from sqlalchemy.orm import Session

from errors import exception_handler
from models import models
from schemas import schemas


def create_rss_entry(db: Session, rss_url: str, rss_header: str) -> models.Rss:
    """
    Func creates a rss source entry in the database with specified arguments
    :param db: sqlalchemy session object
    :param rss_url: rss source url
    :param rss_header: rss source header
    :return:
    """
    db_rss = models.Rss(rss_url=rss_url,
                        rss_header=rss_header)
    db.add(db_rss)
    db.commit()
    db.refresh(db_rss)
    return db_rss


def create_rss(db: Session, rss: schemas.Rss) -> models.Rss:
    """
    Creates a rss source entry in the database according to rss schema
    :param db: sqlalchemy session object
    :param rss: rss schema
    :return:
    """
    db_rss = models.Rss(rss_url=rss.rss_url,
                        rss_header=rss.rss_header)
    db.add(db_rss)
    db.commit()
    db.refresh(db_rss)
    return db_rss


def delete_rss_source(db: Session, rss_source_id: int) -> None:
    """
    Delete rss source entry in the database
    :param db: sqlalchemy session object
    :param rss_source_id: rss source id in the database (schemas.Rss.id)
    :return:
    """
    rss_source = db.query(models.Rss).filter(models.Rss.id == rss_source_id).first()
    db.delete(rss_source)
    db.commit()


def get_rss_source_by_url(db: Session, rss_url: str):
    """
    Get rss source entry by it's url from the database
    :param db: sqlalchemy session object
    :param rss_url: rss source url
    :return:
    """
    return db.query(models.Rss).filter(models.Rss.rss_url == rss_url).first()


def get_rss_source_by_id(db: Session, rss_id: int):
    """
    Get rss source entry by it's id from the database
    :param db: sqlalchemy session object
    :param rss_id: rss source id
    :return:
    """
    return db.query(models.Rss).filter(models.Rss.id == rss_id).first()


def get_all_rss_sources(db: Session):
    """
    Get all rss sources from the database
    :param db: sqlalchemy session object
    :return: sqlalchemy session object
    """
    return db.query(models.Rss).all()


def create_news_entry(db: Session, news: schemas.News, rss_id: int):
    """
    Create a news entry in the database according to schema
    :param db: sqlalchemy session object
    :param news: News schema with data
    :param rss_id: rss source id
    :return:
    """
    news = models.News(**news, rss_source=rss_id)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def get_news_by_title(db: Session, title: str):
    """
    Get news by title
    :param db: sqlalchemy session object
    :param title: news title
    :return:
    """
    return db.query(models.News).filter(models.News.title == title).first()


def get_news_by_date_source(db: Session,
                            pubdate: Optional[str] = None,
                            source: Optional[str] = None,
                            limit_arg: Optional[int] = None):
    """
    Get news by date and/or rss source from the database
    :param db: sqlalchemy session object
    :param pubdate: news publication date
    :param source: rss source url
    :param limit_arg: limit number of news
    :return:
    """
    if source is None:
        return get_news_by_date(db=db, pubdate=pubdate, limit_arg=limit_arg)
    rss_source_id = db.query(models.Rss).filter(models.Rss.rss_url == source).first()
    if rss_source_id is None:
        raise exception_handler.NewsNotFound
    query_by_source_id = db.query(models.News).filter(models.News.rss_source == rss_source_id.id)
    if pubdate is None:
        return query_by_source_id.limit(limit_arg).all()
    return query_by_source_id.filter(models.News.pubdate_format == pubdate).limit(limit_arg).all()


def get_news_by_date(db: Session,
                     pubdate: Any,
                     limit_arg: Optional[int] = None):
    """
    Get news by date from the database
    :param db: sqlalchemy session object
    :param pubdate: news publication date
    :param limit_arg: limit number of news
    :return:
    """
    if pubdate is None:
        return get_all_news(db=db, limit_arg=limit_arg)
    return db.query(models.News).filter(models.News.pubdate_format == pubdate).limit(limit_arg).all()


def get_news_by_source_id(db: Session,
                          rss_source_id: str,
                          limit_arg: Optional[int] = None):
    """
    Get news by source id and limit output
    :param db: sqlalchemy session object
    :param rss_source_id: rss source id
    :param limit_arg: limit number of news
    :return:
    """
    return db.query(models.News).filter(models.News.rss_source == rss_source_id).limit(limit_arg).all()


def get_all_news(db: Session, limit_arg: Optional[int] = None):
    """
    Get all news entries from the database and limit the output
    :param db: sqlalchemy session object
    :param limit_arg: limit number of news
    :return:
    """
    return db.query(models.News).limit(limit_arg).all()


def delete_news_by_id(db: Session, news_id: int):
    """
    Delete news entry from the database by news id
    :param db: sqlalchemy session object
    :param news_id: news id in the database
    :return:
    """
    db.query(models.News).filter(models.News.id == news_id).delete()
    db.commit()
