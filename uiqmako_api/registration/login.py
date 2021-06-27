from datetime import datetime, timedelta
from config import settings
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .schemas import TokenData, UserInDB, User
from peewee_async import Manager
from ..dependencies import get_db
from ..models.login import get_user
from ..exceptions import LoginException, ExpiredTokenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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


async def get_current_user(token: str = Depends(oauth2_scheme), db: Manager = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise LoginException
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        raise ExpiredTokenException
    except JWTError as e:
        raise LoginException
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise LoginException
    return User.from_orm(user)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

