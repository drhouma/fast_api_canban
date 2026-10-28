from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.services.tasks import TaskService, get_task_service
from app.db.database import get_db
from app.repositories.tasks import get_task_repo
from app.schemas.tasks import TaskCreate, TaskUpdate

task_router = APIRouter(tags=["tasks"])

task_service_type = Annotated[TaskService, Depends(get_task_repo)]

@task_router.get("/tasks")
def get_tasks(task_service: task_service_type):
    return {"tasks": task_service.get_all()}

@task_router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_service: Annotated[TaskService, Depends(get_task_repo)], task_data: TaskCreate):
    task_service.create_task(task_data)


@task_router.put("/tasks/{task_id}", status_code=status.HTTP_202_ACCEPTED)
def update_task(task_service: task_service_type, task_id: int, task_data: TaskUpdate):
    return task_service.update_task(task_id, task_data)


@task_router.delete("/tasks/{task_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_task(task_service: task_service_type, task_id: int):
    return task_service.delete_task(task_id)