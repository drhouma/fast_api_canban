
from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from app.repositories.board import BoardRepository, get_board_repo
from app.schemas.board import BoardCreate, BoardUpdate


class BoardService:
    def __init__(self, repo: BoardRepository):
        self.repo = repo

    # Get all boards belonging to user
    def get_user_boards(self, user_id: int):
        return self.repo.get_user_boards(user_id)

    # Check membership and return board
    def get_board(self, board_id: int, user_id: int):
        membership = self.repo.get_user_board(
            user_id=user_id,
            board_id=board_id
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        return self.repo.get_board_by_id(board_id)

    # Create board and assign creator as owner
    def create_board(self, board_data: BoardCreate, user_id: int):
        return self.repo.create_board(
            title=board_data.title,
            description=board_data.description,
            user_id=user_id,
            is_personal=board_data.is_personal
        )

    # Update board
    def update_board(
        self,
        board_id: int,
        user_id: int,
        board_data: BoardUpdate
    ):
        membership = self._get_membership(board_id, user_id)

        if membership.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this board"
            )

        board = self.repo.get_board_by_id(board_id)

        update_data = board_data.model_dump(exclude_unset=True)

        if not update_data:
            return board

        return self.repo.update_board(board, update_data)

    # Delete board
    def delete_board(self, board_id: int, user_id: int):
        membership = self._get_membership(board_id, user_id)

        if membership.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can delete this board"
            )

        self.repo.delete_board(board_id)

    # Internal membership check
    def _get_membership(self, board_id: int, user_id: int):
        membership = self.repo.get_user_board(
            user_id=user_id,
            board_id=board_id
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found"
            )

        return membership


def get_board_service(
    repo: Annotated[BoardRepository, Depends(get_board_repo)]
):
    return BoardService(repo)
