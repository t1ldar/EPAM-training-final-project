"""Module defines database connection and communication"""
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def wait_for_db(db_url):
    """
    Checks if database connection is established
    :param db_url: database url
    :return: None
    """
    _local_engine = create_engine(db_url)
    _LocalSessionLocal = sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=_local_engine)
    up = False
    while not up:
        try:
            # Try to create session to check if DB is awake
            db_session = _LocalSessionLocal()
            # try some query
            db_session.execute("SELECT 1")
            db_session.commit()
        except Exception as err:
            print(f"Connection error: {err}")
            up = False
        else:
            up = True
        time.sleep(1)


HOST_DB = 'db-pg'
PORT = 5432
POSTGRES_USER = 'unicorn.user'
POSTGRES_PASSWORD = 'magical_password'
POSTGRES_DB = 'rainbow_database'
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST_DB}:5432/{POSTGRES_DB}"
# Wait and recheck until container with postgres is up
wait_for_db(SQLALCHEMY_DATABASE_URL)
# Create sqlalchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a session object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
