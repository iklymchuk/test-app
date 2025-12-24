from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from hotel.db.models import Base

engine: Engine = None
DBSession: sessionmaker = None


def init_db(db_url: str):
    global engine, DBSession
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
