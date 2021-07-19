from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt, ExpiredSignatureError
from typing import Optional
from passlib.context import CryptContext
from config import settings
from uiqmako_api.schemas.users import TokenData, UserInDB, User, UserCategory
from peewee_async import Manager #TODO: treureho
from uiqmako_api.api.dependencies import get_db #TODO: treureho
from uiqmako_api.models.users import get_user, create_user, update_user_orm
from uiqmako_api.errors.exceptions import LoginException, ExpiredTokenException

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


async def check_current_active_user_is_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.category != UserCategory.ADMIN:
        raise HTTPException(status_code=401, detail="Permission denied")
    return True


async def return_acces_token(user: User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


async def add_user(username: str, password: str, db: Manager = Depends(get_db)):
    user_exists = await get_user(db, username)
    if user_exists:
        raise Exception("Username already in use") #TODO: choose exception
    return await create_user(db, username, get_password_hash(password))


async def update_user(userdata: User, db: Manager = Depends(get_db)):
    result = await update_user_orm(db, userdata)
    return result
