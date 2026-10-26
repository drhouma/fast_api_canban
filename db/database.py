from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, session, DeclarativeBase
from app.db.settings import DbSettings, DbLibs

settings = DbSettings(lib = DbLibs.psycopg)

sync_engine = create_engine(url=settings.conn_string, echo=True, pool_size=5,max_overflow=10)

async_engine = create_async_engine(url=settings.conn_string, echo=True, pool_size=5,max_overflow=10)

class Base(DeclarativeBase):
    pass

sessionLocal = sessionmaker(sync_engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(sync_engine)


def delete_tables():
    Base.metadata.drop_all(sync_engine)