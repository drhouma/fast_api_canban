
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.task import Task


class TasksRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_board(self, board_id: int):
        stmt = select(Task).where(Task.board_id == board_id)
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, task_id: int):
        return self.db.get(Task, task_id)

    def get_by_id_and_board(self, task_id: int, board_id: int):
        stmt = select(Task).where(
            Task.id == task_id,
            Task.board_id == board_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_task(self, board_id: int, task_data: dict):
        try:
            task = Task(
                **task_data,
                board_id=board_id
            )
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception:
            self.db.rollback()
            raise

    def update_task(self, task: Task, update_data: dict):
        try:
            for key, value in update_data.items():
                setattr(task, key, value)

            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception:
            self.db.rollback()
            raise

    def delete_task(self, task: Task):
        try:
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise


def get_task_repo(
    db: Annotated[Session, Depends(get_db)]
):
    return TasksRepository(db)
