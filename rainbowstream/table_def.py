from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///rainbow.db', echo=False)
Base = declarative_base()

class Map(Base):

    __tablename__ = "map"

    rainbow_id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer)

    def __init__(self, tweet_id):
        self.tweet_id = tweet_id

Base.metadata.create_all(engine)