from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

from app.db.database import create_tables, get_db, sync_engine, delete_tables
from contextlib import asynccontextmanager, contextmanager
from app.routers.tasks import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan worked correctly")
    create_tables()
    try:
        yield
    finally:
        print("lifespan exit sequence")
        delete_tables()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

