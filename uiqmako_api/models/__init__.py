import peewee_async
from config import settings

database = peewee_async.PostgresqlDatabase(
    database=settings.DB_CONFIG.NAME,
    host=settings.DB_CONFIG.HOST,
    port=settings.DB_CONFIG.PORT,
    user=settings.DB_CONFIG.USER,
    password=settings.DB_CONFIG.PWD,
)


def get_db_manager():
    objects = peewee_async.Manager(database)
    database.set_allow_sync(False)
    return objects


def setup_database(safe=True):
    from uiqmako_api.models.edits import TemplateEditModel
    from uiqmako_api.models.users import UserModel
    from uiqmako_api.models.templates import CaseModel, TemplateInfoModel
    with get_db_manager().allow_sync():
        TemplateInfoModel.create_table(safe)
        CaseModel.create_table(safe)
        UserModel.create_table(safe)
        TemplateEditModel.create_table(safe)
    database.close()


def drop_database():
    from .templates import TemplateInfoModel, CaseModel
    from .edits import TemplateEditModel
    from .users import UserModel
    with get_db_manager().allow_sync():
        TemplateEditModel.drop_table(cascade=True)
        TemplateInfoModel.drop_table(cascade=True)
        CaseModel.drop_table(cascade=True)
        UserModel.drop_table(cascade=True)
    database.close()

