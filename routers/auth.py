from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from app.schemas.auth import TokenResponse

auth_router = APIRouter()

from app.services.auth import AuthService, get_auth_service

@auth_router.post("/auth/login", tags=["auth"], response_model=TokenResponse)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],
          auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    email = form.username.strip().lower()
    user = auth_service.authenticate_user(email=email, password=form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_service.create_access_token(user.id),
        "token_type": "bearer",
    }