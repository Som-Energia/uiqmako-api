from .models.models import *
from .schemas import *
from peewee_async import Manager
from .models.models import TemplateInfoModel
from peewee import DoesNotExist


async def get_all_templates_orm(db: Manager):
    templates = await db.execute(TemplateInfoModel.select())
    result = [TemplateInfoBase.from_orm(t) for t in templates]
    return result


async def get_template_orm(db, template_id=None, erp_id=None, xml_id=None, name=None):
    search_fields = {}
    if template_id:
        search_fields.update({'template_id': template_id})
    if erp_id:
        search_fields.update({'erp_id': erp_id})
    if xml_id:
        search_fields.update({'xml_id': xml_id})
    if name:
        search_fields.update({'name': name})
    try:
        template_info = await db.get(TemplateInfoModel, **search_fields)
        return TemplateInfoBase.from_orm(template_info)
    except DoesNotExist as ex:
        return None


async def add_or_get_template_orm(db, name, xml_id, erp_id=None):
    created = False
    template_info = await get_template_orm(db, xml_id=xml_id)
    if not template_info and erp_id:
        template_info = await get_template_orm(db, erp_id=erp_id)
    if not template_info and name:
        template_info = await get_template_orm(db, name=name)
    if not template_info:
        template_info, created = await db.create_or_get(
            TemplateInfoModel,
            name=name, model='poweremail.templates', xml_id=xml_id, erp_id=erp_id
        )

    return created, template_info
