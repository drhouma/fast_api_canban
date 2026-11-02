from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from select import select
from sqlalchemy.orm import Session
from starlette import status

from app.models.user import User
from app.db.database import get_db
from app.repositories.user import UserRepository, get_user_repo
password_hash = PasswordHash.recommended()

SECRET_KEY = "SECRET_KEY"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

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



    # need to check if given user_id exist
    @classmethod
    def create_access_token(cls, user_id: int):
        expire = datetime.now() + timedelta(minutes=15)

        payload = {
            "exp": expire,
            "sub": str(user_id),
        }

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm="HS256"
        )
        return token

    def get_current_user(
            self,
            token: Annotated[str, Depends(oauth2_scheme)]
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms="HS256",
            )

            user_id = payload.get("sub")

            if user_id is None:
                raise credentials_exception

            user_id = int(user_id)

        except (ValueError, TypeError):
            raise credentials_exception

        user = self.user_repo.get_user_by_id(user_id)

        if user is None:
            raise credentials_exception

        return user

    def register_user(self):
        pass


def get_auth_service(user_repo: Annotated[UserRepository, Depends(get_user_repo)]):
    return AuthService(user_repo)

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = auth_service.user_repo.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user