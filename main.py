from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

from app.db.database import get_db, sync_engine
from app.db.on_start import create_tables, delete_tables, insert_data
from contextlib import asynccontextmanager, contextmanager
from app.routers.tasks import task_router
from app.routers.auth import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan worked correctly")
    create_tables()
    insert_data()
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

app.include_router(task_router)
app.include_router(auth_router)

