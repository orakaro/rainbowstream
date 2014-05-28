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
        res = session.query(Map).filter("rainbow_id =:rid").params(rid=rid).all()
        return res

    def tweet_query(self, tid):
        """
        Query base of tweet id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Map).filter("tweet_id =:tid").params(tid=tid).all()
        return res

    def truncate(self):
        """
        Truncate table
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.query(Map).delete()
        session.commit()
