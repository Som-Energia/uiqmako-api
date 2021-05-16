import peewee_async
from config import settings

database = peewee_async.PostgresqlDatabase(
    database=settings.DB_NAME,
)


def get_db_manager():
    objects = peewee_async.Manager(database)
    database.set_allow_sync(False)
    return objects


def setup_database(safe=True):
    from .models import TemplateInfoModel, CaseModel, TemplateEditModel
    from .login import UserModel
    TemplateInfoModel.create_table(safe)
    CaseModel.create_table(safe)
    UserModel.create_table(safe)
    TemplateEditModel.create_table(safe)
    database.close()


def drop_database():
    from .models import TemplateInfoModel, CaseModel, TemplateEditModel
    from .login import UserModel
    with get_db_manager().allow_sync():
        TemplateEditModel.drop_table()
        TemplateInfoModel.drop_table()
        CaseModel.drop_table()
        UserModel.drop_table()
    database.close()

