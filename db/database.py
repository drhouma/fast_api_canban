from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, session, DeclarativeBase
from app.db.settings import DbSettings, DbLibs

settings = DbSettings(lib = DbLibs.psycopg)

sync_engine = create_engine(url=settings.conn_string, echo=True, pool_size=5,max_overflow=10)

async_engine = create_async_engine(url=settings.conn_string, echo=True, pool_size=5,max_overflow=10)


convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    pass

sessionLocal = sessionmaker(sync_engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
