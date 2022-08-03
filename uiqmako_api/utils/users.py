from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from passlib.context import CryptContext
from config import settings
from uiqmako_api.errors.exceptions import UsernameExists
from uiqmako_api.schemas.users import User, TokenInPost
from uiqmako_api.schemas.templates import TemplateInfoBase
from uiqmako_api.models.users import (
    get_user,
    create_user,
    update_user_orm,
    get_user_edited_templates_orm
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode['exp'] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_pwd):
        return False
    return user


async def return_access_token(user: User):
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return TokenInPost(access_token=access_token)


async def add_user(username: str, password: str):
    user_exists = await get_user(username)
    if user_exists:
        raise UsernameExists
    return await create_user(username, get_password_hash(password))


async def update_user(userdata: User):
    result = await update_user_orm(userdata)
    return result

async def get_user_edited_templates(user_id: int):
    templates = await get_user_edited_templates_orm(user_id)
    return [TemplateInfoBase.from_orm(t) for t in templates]
