from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from app.models.task import Task
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.tasks import TaskCreate

class TasksRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        stmt = select(Task)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def create_task(self, task_data: TaskCreate):
        task = Task(**task_data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

def get_task_repo(session: Annotated[Session, Depends(get_db)]):
    return TasksRepository(session)