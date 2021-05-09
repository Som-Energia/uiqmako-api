from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserCategory(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    username: str
    disabled: Optional[bool] = None
    category: Optional[UserCategory] = UserCategory.USER
    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_pwd: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
