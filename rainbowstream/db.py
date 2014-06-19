import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .table_def import *


class RainbowDB():

    engine = None

    def __init__(self):
        if not os.path.isfile('rainbow.db'):
            init_db()
        self.engine = create_engine('sqlite:///rainbow.db', echo=False)

    def tweet_store(self, tweet_id):
        """
        Store tweet id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        m = Tweet(tweet_id)
        session.add(m)
        session.commit()

    def rainbow_to_tweet_query(self, rid):
        """
        Query base of rainbow id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Tweet).filter_by(rainbow_id=rid).all()
        return res

    def tweet_to_rainbow_query(self, tid):
        """
        Query base of tweet id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Tweet).filter_by(tweet_id=tid).all()
        return res

    def message_store(self, message_id):
        """
        Store message id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        m = Message(message_id)
        session.add(m)
        session.commit()

    def rainbow_to_message_query(self, rid):
        """
        Query base of rainbow id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Message).filter_by(rainbow_id=rid).all()
        return res

    def message_to_rainbow_query(self, mid):
        """
        Query base of message id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Message).filter_by(message_id=mid).all()
        return res
