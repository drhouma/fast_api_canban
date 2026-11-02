
from typing import Annotated

from fastapi import Depends, HTTPException

from app.repositories.tasks import TasksRepository, get_task_repo
from app.repositories.board import BoardRepository, get_board_repo
from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self,
        task_repo: TasksRepository,
        board_repo: BoardRepository
    ):
        self.task_repo = task_repo
        self.board_repo = board_repo

    def get_board_tasks(self, board_id: int, user_id: int):
        self._check_membership(board_id, user_id)
        return self.task_repo.get_all_by_board(board_id)

    def get_task(self, board_id: int, task_id: int, user_id: int):
        self._check_membership(board_id, user_id)

        task = self._get_task_or_404(task_id, board_id)
        return task

    def create_task(
        self,
        board_id: int,
        user_id: int,
        task_data: TaskCreate
    ):
        self._check_membership(board_id, user_id)

        return self.task_repo.create_task(
            board_id=board_id,
            task_data=task_data.model_dump()
        )

    def update_task(
        self,
        board_id: int,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
    ):
        self._check_membership(board_id, user_id)

        task = self._get_task_or_404(task_id, board_id)

        update_data = task_data.model_dump(exclude_unset=True)

        if not update_data:
            return task

        return self.task_repo.update_task(task, update_data)

    def delete_task(
        self,
        board_id: int,
        task_id: int,
        user_id: int
    ):
        self._check_membership(board_id, user_id)

        task = self._get_task_or_404(task_id, board_id)

        self.task_repo.delete_task(task)

    def _check_membership(self, board_id: int, user_id: int):
        membership = self.board_repo.get_user_board(
            user_id=user_id,
            board_id=board_id
        )

        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="Board not found"
            )

        return membership

    def _get_task_or_404(self, task_id: int, board_id: int):
        task = self.task_repo.get_by_id_and_board(
            task_id=task_id,
            board_id=board_id
        )

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return task


def get_task_service(
    task_repo: Annotated[TasksRepository, Depends(get_task_repo)],
    board_repo: Annotated[BoardRepository, Depends(get_board_repo)]
):
    return TaskService(task_repo, board_repo)
