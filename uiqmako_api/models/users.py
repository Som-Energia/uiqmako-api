from . import database
import peewee
from peewee_async import Manager
from peewee import DoesNotExist
from uiqmako_api.schemas.users import UserCategory, User


class UserModel(peewee.Model):
    id = peewee.AutoField()
    username = peewee.CharField(unique=True)
    hashed_pwd = peewee.CharField()
    disabled = peewee.BooleanField()
    category = peewee.CharField()

    class Meta:
        database = database
        table_name = "users"


async def get_user(db: Manager, username: str):
    try:
        user = await db.get(UserModel, username=username)
    except DoesNotExist as ex:
        return False
    return user


async def create_user(db: Manager, username: str, password_hash):
    user, created = await db.create_or_get(
        UserModel,
        username=username, hashed_pwd=password_hash, category=UserCategory.BASIC_USER,
        disabled=False
    )
    return user


async def get_users_list(db: Manager):
    users = await db.execute(UserModel.select())
    result = [User.from_orm(t) for t in users]
    return result


async def update_user_orm(db: Manager, userdata):
    user_exists = await get_user(db, userdata.username)
    if user_exists:
        user_exists.category = userdata.category
        user_exists.disabled = userdata.disabled
    await db.update(user_exists, only=['category', 'disabled'])
