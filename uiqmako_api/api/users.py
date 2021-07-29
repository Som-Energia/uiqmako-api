from fastapi import APIRouter, Depends, Form
from peewee_async import Manager
from uiqmako_api.schemas.users import User, UserInPost
from .dependencies import get_db, check_current_active_user_is_admin
from uiqmako_api.utils.users import (
    add_user,
    return_access_token,
    update_user
)
from uiqmako_api.models.users import get_users_list


router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.post("")
async def add_new_user(username: str = Form(...), password: str = Form(...), db: Manager = Depends(get_db)):
    user = await add_user(username, password, db)
    token = await return_access_token(user)
    return token


@router.get("")
async def get_users(is_admin: User = Depends(check_current_active_user_is_admin), db: Manager = Depends(get_db)):
    user_list = list(filter(lambda x: x.username != 'admin', (await get_users_list(db))))
    user_list.sort(key=lambda x: x.username)
    return user_list


@router.put("")
async def update_users(
    userdata: UserInPost,
    is_admin: User = Depends(check_current_active_user_is_admin),
    db: Manager = Depends(get_db)
):
    result = await update_user(userdata, db)
    return result
