from datetime import datetime, timedelta
from fastapi import Depends
from jose import jwt
from typing import Optional
from passlib.context import CryptContext
from config import settings
from uiqmako_api.errors.exceptions import UsernameExists
from uiqmako_api.schemas.users import User, TokenInPost
from peewee_async import Manager
from uiqmako_api.api.dependencies import get_db
from uiqmako_api.models.users import get_user, create_user, update_user_orm


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


async def authenticate_user(username: str, password: str, db: Manager = Depends(get_db)):
    user = await get_user(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_pwd):
        return False
    return user


async def return_access_token(user: User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return TokenInPost(access_token=access_token)


async def add_user(username: str, password: str, db: Manager = Depends(get_db)):
    user_exists = await get_user(db, username)
    if user_exists:
        raise UsernameExists
    return await create_user(db, username, get_password_hash(password))


async def update_user(userdata: User, db: Manager = Depends(get_db)):
    result = await update_user_orm(db, userdata)
    return result
