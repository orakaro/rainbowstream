import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from table_def import Map
from .table_def import *


class RainbowDB():

    engine = None

    def __init__(self):
        if not os.path.isfile('rainbow.db'):
            init_db()
        self.engine = create_engine('sqlite:///rainbow.db', echo=False)

    def store(self, tweet_id):
        """
        Store tweet id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        m = Map(tweet_id)
        session.add(m)
        session.commit()

    def rainbow_query(self, rid):
        """
        Query base of rainbow id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Map).filter_by(rainbow_id=rid).all()
        return res

    def tweet_query(self, tid):
        """
        Query base of tweet id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Map).filter_by(tweet_id=tid).all()
        return res