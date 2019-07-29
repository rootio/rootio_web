from sqlalchemy.orm import sessionmaker


class DBAgent(object):
    """
    Database connection agent
    """

    def __init__(self, engine):
        print "DBA inited..."
        self.__engine = engine
        self.__session = None
        self.__close_on_exit = False;

    def __enter__(self):
        print "Session started"
        self.__session = sessionmaker(bind=self.__engine)()
        return self

    def session(self, reusable=True):
        if not reusable:
            self.__close_on_exit = True
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__close_on_exit:
            self.session.close()