import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session


class Engine(object):
    def __init__(self, db_url: str):
        """
        Init database engine
        :param db_url:  example: postgresql://user:password@192.168.0.1/securities
        :type db_url:  str
        """

        self.__engine = db.create_engine(db_url)
        self.__Session = sessionmaker(bind=self.__engine)

    def session(self) -> Session:
        return self.__Session()
