from enum import Enum

class DbLibs(Enum):
    asyncpg = "asyncpg"
    psycopg = "psycopg"

class DbSettings:
    def __init__(self, lib: DbLibs):
        self.LIB = lib

    LIB = "psycopg"
    # LIB="asyncpg"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    conn_string = f"postgresql+{LIB}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"