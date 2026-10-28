from typing import Annotated

from fastapi import Depends
from pydantic.v1 import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.database import get_db

class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    # return User instance with given email if it exist
    # else return None
    def get_user_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt).scalars().one_or_none()
        return result


def get_user_repo(db: Annotated[Session, Depends(get_db)]) :
    return UserRepository(db)