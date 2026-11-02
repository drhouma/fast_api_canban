
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from app.services.tasks import TaskService, get_task_service
from app.services.auth import get_current_user


task_router = APIRouter(
    prefix="/boards/{board_id}/tasks",
    tags=["Tasks"]
)


@task_router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)

def create_task(
    board_id: int,
    task_data: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)]
):

    return service.create_task(
        board_id=board_id,
        user_id=current_user.id,
        task_data=task_data
    )


@task_router.get(
    "",
    response_model=list[TaskResponse]
)
def get_board_tasks(
    board_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)]
):
    return service.get_board_tasks(
        board_id=board_id,
        user_id=current_user.id
    )


@task_router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    board_id: int,
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)]
):
    return service.get_task(
        board_id=board_id,
        task_id=task_id,
        user_id=current_user.id
    )


@task_router.patch(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    board_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)]
):
    return service.update_task(
        board_id=board_id,
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data
    )


@task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    board_id: int,
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)]
):
    service.delete_task(
        board_id=board_id,
        task_id=task_id,
        user_id=current_user.id
    )

    return None
