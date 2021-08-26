import pytest

from uiqmako_api.models.users import get_users_list
from uiqmako_api.schemas.users import UserCategory
from uiqmako_api.utils.users import *
from uiqmako_api.errors.http_exceptions import LoginException


@pytest.mark.asyncio
class TestUsers:

    async def test_create_access_token_not_registered(self):
        from uiqmako_api.api.dependencies import get_current_user

        token = create_access_token({'sub': 'inexisting'})
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded['sub'] == 'inexisting'

        with pytest.raises(LoginException):
            await get_current_user(token)

    async def test_create_access_token_registered(self):
        from uiqmako_api.api.dependencies import get_current_user

        token = create_access_token({'sub': 'UserAll'})
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded['sub'] == 'UserAll'

        user = await get_current_user(token)
        assert user.username == 'UserAll'

    async def test_add_user_exists(self):
        with pytest.raises(UsernameExists):
            await add_user('UserAll', 'fakepwd')

    async def test_add_user_ok(self):
        created = await add_user('NewUser', 'fakepwd')

        user = await get_user('NewUser')

        assert created.username == user.username

    async def test_update_user_data(self):
        user_pre = await get_user('NewUser')
        changed_user = User(id=user_pre.id, username=user_pre.username, category=UserCategory.ADMIN, disabled=True)
        await update_user(changed_user)
        user_post = await get_user('NewUser')
        assert user_pre.username == user_post.username
        assert user_pre.category != user_post.category
        assert user_post.category == UserCategory.ADMIN
        assert user_pre.disabled != user_post.disabled
        assert user_post.disabled
