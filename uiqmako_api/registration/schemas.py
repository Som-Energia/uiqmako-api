from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserCategory(str, Enum):
    BASIC_USER = "basic_user"
    HTML_USER = "html_user"
    PYTHON_USER = "python_user"
    ADMIN = "admin"


class User(BaseModel):
    id: int
    username: str
    disabled: Optional[bool] = None
    category: Optional[UserCategory] = UserCategory.BASIC_USER
    class Config:
        orm_mode = True

    def get_allowed_fields(self):
        basic_fields = ['content', 'def_subject', 'def_bcc']
        if self.category == UserCategory.HTML_USER:
            basic_fields += ['html']
        if self.category == UserCategory.PYTHON_USER:
            basic_fields += ['html', 'python', 'lang', 'def_body_text', 'def_to', 'def_cc']
        return basic_fields


class UserInDB(User):
    hashed_pwd: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

