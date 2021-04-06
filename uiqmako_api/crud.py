from .models import *
from .schemas import *
from peewee_async import Manager

async def get_all_templates(db: Manager):
    templates = await db.execute(TemplateInfoModel.select())
    result = [TemplateInfoBase.from_orm(t) for t in templates]
    return result