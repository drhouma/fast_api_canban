from typing import Annotated
from fastapi import Depends
from sqlalchemy import select, update
from app.models.task import Task
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.tasks import TaskCreate, TaskUpdate

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

    def update_task(self, task_id, task_data: TaskUpdate):
        # stmt = update(Task).where(Task.id == task_data.t_id).values(status = task_data.new_status)
        task = self.db.get(Task, task_id)
        task.status = task_data.new_status
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int):
        task = self.db.get(Task, task_id)
        self.db.delete(task)
        self.db.commit()
        return True

def get_task_repo(session: Annotated[Session, Depends(get_db)]):
    return TasksRepository(session)