from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///rainbow.db', echo=False)
Base = declarative_base()


class Tweet(Base):

    __tablename__ = "tweet"

    rainbow_id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer)

    def __init__(self, tweet_id):
        self.tweet_id = tweet_id


class Message(Base):

    __tablename__ = "message"

    rainbow_id = Column(Integer, primary_key=True)
    message_id = Column(Integer)

    def __init__(self, message_id):
        self.message_id = message_id


class Theme(Base):

    __tablename__ = "theme"

    theme_id = Column(Integer, primary_key=True)
    theme_name = Column(String(20))

    def __init__(self, theme_name):
        self.theme_name = theme_name


class List(Base):

    __tablename__ = "list"

    list_rid = Column(Integer, primary_key=True)
    list_id = Column(Integer)
    list_name = Column(String(50))

    def __init__(self, list_id, list_name):
        self.list_id = list_id
        self.list_name = list_name


def init_db():
    Base.metadata.create_all(engine)
