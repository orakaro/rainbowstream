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


def init_db():
    Base.metadata.create_all(engine)
