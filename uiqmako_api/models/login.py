from . import database
import peewee
from peewee_async import Manager


class UserModel(peewee.Model):
    id = peewee.AutoField()
    username = peewee.CharField(unique=True)
    hashed_pwd = peewee.CharField()
    active = peewee.BooleanField()
    class Meta:
        database = database
        table_name = "users"


async def get_user(db: Manager, username: str):
    user = await db.get(UserModel, username=username)
    return user
