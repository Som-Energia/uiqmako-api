from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from fastapi import Form


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
        if self.disabled:
            return []
        basic_fields = ['content', 'def_subject', 'def_bcc', 'html']
        if self.category in [UserCategory.PYTHON_USER, UserCategory.ADMIN]:
            basic_fields += ['python', 'lang', 'def_body_text', 'def_to', 'def_cc']
        return basic_fields


class UserInPost(User):

    def __init__(self, id: int = Form(...), username: str = Form(...),
                 disabled: Optional[bool] = Form(...), category: Optional[UserCategory] = Form(...)
                 ):
        super().__init__(id=id, username=username, disabled=disabled, category=category)


class UserInDB(User):
    hashed_pwd: str

    class Config:
        orm_mode = True


class TokenInPost(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserInfo(User):
    allowed_fields: List[str] = []

    def __init__(self, user: User):
        super().__init__(**user.__dict__)
        self.allowed_fields = user.get_allowed_fields()