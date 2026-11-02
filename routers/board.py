
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse
from app.services.board import BoardService, get_board_service
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/boards",
    tags=["Boards"]
)


@router.post(
    "",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED
)
def create_board(
    board_data: BoardCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BoardService, Depends(get_board_service)]
):
    return service.create_board(
        board_data=board_data,
        user_id=current_user.id
    )


@router.get(
    "",
    response_model=list[BoardResponse]
)
def get_my_boards(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BoardService, Depends(get_board_service)]
):
    return service.get_user_boards(current_user.id)


@router.get(
    "/{board_id}",
    response_model=BoardResponse
)
def get_board(
    board_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BoardService, Depends(get_board_service)]
):
    return service.get_board(
        board_id=board_id,
        user_id=current_user.id
    )


@router.patch(
    "/{board_id}",
    response_model=BoardResponse
)
def update_board(
    board_id: int,
    board_data: BoardUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BoardService, Depends(get_board_service)]
):
    return service.update_board(
        board_id=board_id,
        user_id=current_user.id,
        board_data=board_data
    )


@router.delete(
    "/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_board(
    board_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BoardService, Depends(get_board_service)]
):
    service.delete_board(
        board_id=board_id,
        user_id=current_user.id
    )

    return None
