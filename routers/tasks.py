from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.services.tasks import TaskService, get_task_service
from app.db.database import get_db
from app.repositories.tasks import get_task_repo
from app.schemas.tasks import TaskCreate

router = APIRouter(tags=["tasks"])



@router.get("/tasks")
def get_tasks(task_service: Annotated[TaskService, Depends(get_task_repo)]):
    return {"tasks": task_service.get_all()}

@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_service: Annotated[TaskService, Depends(get_task_repo)], task_data: TaskCreate):
    task_service.create_task(task_data)
