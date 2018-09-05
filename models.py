from sqlalchemy import create_engine, Column, Integer, DECIMAL, Date, Float, VARCHAR, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from job_scrapy.settings import DATABASE

DeclarativeBase = declarative_base()


def db_connect():
    return create_engine(URL(**DATABASE))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class JobInfo(DeclarativeBase):
    __tablename__ = 'job_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column('title', Text)
    company = Column('company', Text)
    city = Column('city', Text)
    zip = Column('zip', Integer, nullable=True)
    description = Column('description', Text)
    text_html = Column('text_html', Text)
    posted_date = Column('posted_date', Date)
    stars = Column('stars', Float)
    original_url = Column('original_url', Text)
    post_url = Column('post_url', Text, unique=True)
    min_salary = Column('min_salary', DECIMAL(10, 3))
    max_salary = Column('max_salary', DECIMAL(10, 3))
    period = Column('period', VARCHAR(10))
    filter_salary = Column('filter_salary', Text)
    sponsored = Column('sponsored', Text)
