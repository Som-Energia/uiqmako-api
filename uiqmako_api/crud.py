from .models import *
from .schemas import *
from peewee_async import Manager

async def get_all_templates(db: Manager):
    templates = await db.execute(TemplateInfoModel.select())
    result = []
    for t in templates:
        print("*"*40)
        print(t)
        a = TemplateInfo.from_orm(t)
        result.append(a)
    return result