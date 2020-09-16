from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from rootio.config import DefaultConfig

class DBAgent:

    engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)

    @staticmethod
    def get_session():
        session = sessionmaker(bind=DBAgent.engine)()
        return session
