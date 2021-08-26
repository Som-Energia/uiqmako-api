from fastapi import APIRouter, Depends, Form
from uiqmako_api.schemas.users import UserInPost, User, UserInfo
from .dependencies import check_current_active_user_is_admin, get_current_active_user
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
async def add_new_user(username: str = Form(...), password: str = Form(...)):
    user = await add_user(username, password)
    token = await return_access_token(user)
    return token


@router.get("", dependencies=[Depends(check_current_active_user_is_admin)])
async def get_users():
    user_list = list(filter(lambda x: x.username != 'admin', (await get_users_list())))
    user_list.sort(key=lambda x: x.username)
    return user_list


@router.put("", dependencies=[Depends(check_current_active_user_is_admin)])
async def update_users(userdata: UserInPost):
    result = await update_user(userdata)
    return result


@router.get("/me")
async def current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserInfo(current_user)
