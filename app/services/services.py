"""Module combines various service functions"""
import os.path

import sqlalchemy
from dateutil import parser

import database


def create_database() -> database.Base:
    """Creates database"""
    return database.Base.metadata.create_all(bind=database.engine)


def get_db() -> database.SessionLocal:
    """Creates a session to a database"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_file_extension(extension: str, filename: str) -> str:
    """
    Function update filename extension
    :param extension: extension
    :param filename: filename
    :return: full filename with an extension
    """
    if not os.path.join(filename).endswith(extension):
        return f"{filename}.{extension}"
    return filename


def create_target_path(folder: str, filename: str, extension: str) -> str:
    """
    Func creates full path to a file and appends extension if it doesn't exist
    :param folder: folder location
    :param filename: filename
    :param extension: filename extension in order to update it
    :return: os path to a file
    """
    if not os.path.join(filename).endswith(extension):
        filename = f"{filename}.{extension}"
    return os.path.join(folder, filename)


def format_pubdate(random_date_format: str) -> str:
    """
    Method formatting date to YYYYMMDD
    :param random_date_format: date in random format
    :return: formatted to YYYYMMDD date
    """
    if random_date_format != 'Empty':
        parsed_date = parser.parse(random_date_format)
        formatted_pubdate = parsed_date.strftime("%Y%m%d")
        return formatted_pubdate
    else:
        return 'Empty'


def object_as_dict(orm_object) -> dict:
    """
    Function is used to convert sqlalchemy.orm object into dict format
    :param orm_object:
    :return: data in dictionary format
    """
    return {c.key: getattr(orm_object, c.key) for c in sqlalchemy.inspect(orm_object).mapper.column_attrs}
