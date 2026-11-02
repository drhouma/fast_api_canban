
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.board import Board, BoardUser


class BoardRepository:
    def __init__(self, db: Session):
        self.db = db

    # Get all boards belonging to user
    def get_user_boards(self, user_id: int):
        stmt = (
            select(Board)
            .join(BoardUser, BoardUser.board_id == Board.id)
            .where(BoardUser.user_id == user_id)
        )

        return self.db.execute(stmt).scalars().all()

    # Get board by ID
    def get_board_by_id(self, board_id: int):
        stmt = select(Board).where(Board.id == board_id)

        return self.db.execute(stmt).scalar_one_or_none()

    # Check whether user belongs to board
    def get_user_board(self, user_id: int, board_id: int):
        stmt = select(BoardUser).where(
            BoardUser.user_id == user_id,
            BoardUser.board_id == board_id
        )

        return self.db.execute(stmt).scalar_one_or_none()

    # Create board and assign creator as owner
    def create_board(
        self,
        title: str,
        description: str | None,
        user_id: int,
        is_personal: bool
    ):
        try:
            board = Board(
                title=title,
                description=description,
                is_personal=is_personal
            )

            self.db.add(board)
            self.db.flush()

            membership = BoardUser(
                user_id=user_id,
                board_id=board.id,
                role="owner"
            )

            self.db.add(membership)

            self.db.commit()
            self.db.refresh(board)

            return board

        except Exception:
            self.db.rollback()
            raise

    # Update board
    def update_board(self, board: Board, update_data: dict):
        try:
            for key, value in update_data.items():
                setattr(board, key, value)

            self.db.commit()
            self.db.refresh(board)

            return board

        except Exception:
            self.db.rollback()
            raise

    # Delete board
    def delete_board(self, board_id: int):
        board = self.get_board_by_id(board_id)

        if board is None:
            return False

        try:
            self.db.delete(board)
            self.db.commit()

            return True

        except Exception:
            self.db.rollback()
            raise


def get_board_repo(
    db: Annotated[Session, Depends(get_db)]
):
    return BoardRepository(db)
