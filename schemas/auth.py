from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from pydantic import EmailStr, Field, BaseModel


# class RegisterSchema(BaseModel):
#     email: EmailStr
#     password: str = Field(min_length=3, max_length=20)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str ="bearer"

# class UserSchema(BaseModel):
#     id: int
#     email: EmailStr