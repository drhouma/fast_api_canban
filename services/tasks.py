from typing import Annotated

from sqlalchemy import select
from app.models.task import Task
from sqlalchemy.orm import Session
from app.repositories.tasks import TasksRepository
from app.repositories.tasks import get_task_repo
from fastapi import Depends

from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repo: TasksRepository):
        self.task_repo = repo

    def get_all(self):
        return self.task_repo.get_all()

    def create_task(self, task_data: TaskCreate):
        return self.task_repo.create_task(task_data)

    def update_task(self, task_id: int, task_data: TaskUpdate):
        return self.task_repo.update_task(task_id, task_data)

    def delete_task(self, task_id: int):
        return self.task_repo.delete_task(task_id)


def get_task_service(repo: Annotated[TasksRepository, Depends(get_task_repo)]):
    return TaskService(repo)