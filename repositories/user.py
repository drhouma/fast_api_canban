from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.models.user import User
from app.db.database import get_db
from app.security import get_password_hash

class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    # return User instance with given email if it exists
    # else return None
    def get_user_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = self.db.execute(stmt).scalars().one_or_none()
        return result

    def get_user_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        result = self.db.execute(stmt).scalars().one_or_none()
        return result

    def create_user(self, username: str, email: str, password: str):
        user = User(
            username= username,
            email = email,
            hashed_password = get_password_hash(password)
        )
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise

        return user

def get_user_repo(db: Annotated[Session, Depends(get_db)]) :
    return UserRepository(db)