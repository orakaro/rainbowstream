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
        t = Tweet(tweet_id)
        session.add(t)
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

    def theme_store(self, theme_name):
        """
        Store theme
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        th = Theme(theme_name)
        session.add(th)
        session.commit()

    def theme_update(self, theme_name):
        """
        Update theme
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Theme).all()
        for r in res:
            r.theme_name = theme_name
        session.commit()

    def theme_query(self):
        """
        Query theme
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(Theme).all()
        return res

    def list_store(self, list_id, list_name):
        """
        Store list id and name
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        l = List(list_id, list_name)
        session.add(l)
        session.commit()

    def list_name_to_id_query(self, list_name):
        """
        Query base of list id
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        res = session.query(List).filter_by(list_name=list_name).all()
        return res

