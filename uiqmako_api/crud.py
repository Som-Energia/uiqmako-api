from .models import *
from .schemas import *
from peewee_async import Manager

async def get_all_templates(db: Manager):
    templates = await db.execute(TemplateInfoModel.select())
    result = [TemplateInfoBase.from_orm(t) for t in templates]
    return result

async def get_template_orm(db, template_id):
    template_info = await db.get(TemplateInfoModel, id=template_id)
    return TemplateInfoBase.from_orm(template_info)