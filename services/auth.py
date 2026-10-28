from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from pwdlib import PasswordHash
from select import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.db.database import get_db
from app.repositories.user import UserRepository, get_user_repo
password_hash = PasswordHash.recommended()

SECRET_KEY = "SECRET_KEY"

class AuthService:

    def __init__(self, user_repo: Annotated[UserRepository, Depends(get_user_repo)]):
        self.user_repo = user_repo

    def authenticate_user(
            self,
            email: str,
            password: str
    ):
        user = self.user_repo.get_user_by_email(email)
        if not user or not password_hash.verify(password, user.hashed_password):
            return None
        return user

    @classmethod
    def create_access_token(cls, user_id: int):
        expire = datetime.now() + timedelta(minutes=15)

        payload = {
            "exp": expire,
            "iat": user_id,
        }

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm="HS256"
        )
        return token


def get_auth_service(user_repo: Annotated[UserRepository, Depends(get_user_repo)]):
    return AuthService(user_repo)


