from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from config import settings
from uiqmako_api.errors.http_exceptions import (
    ERPConnectionException,
    LoginException,
    ExpiredTokenException,
    DisabledUserException, PermissionDeniedException)
from uiqmako_api.models.users import get_user
from uiqmako_api.schemas.users import TokenData, User, UserCategory


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def check_erp_conn():
    from .api import app
    if not app.ERP.get_erp_conn() or not app.ERP.test_connection():
        raise ERPConnectionException()
    return True


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = await get_user(username=token_data.username)
    if not user:
        raise LoginException
    return User.from_orm(user)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise DisabledUserException
    return current_user


async def check_current_active_user_is_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.category != UserCategory.ADMIN:
        raise PermissionDeniedException()
    return True
