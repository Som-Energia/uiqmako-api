from datetime import datetime
from .schemas import *
from peewee_async import Manager
from .models.models import TemplateInfoModel, TemplateEditModel
from .models.login import UserModel
from peewee import DoesNotExist


async def get_all_templates_orm(db: Manager):
    templates = await db.execute(TemplateInfoModel.select())
    result = [TemplateInfoBase.from_orm(t) for t in templates]
    return result


async def get_template_orm(db, template_id=None, erp_id=None, xml_id=None, name=None):
    search_fields = {}
    if template_id:
        search_fields.update({'id': template_id})
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


async def set_last_updated(db, template_id):
    template_obj = await db.get(TemplateInfoModel, id=template_id)
    template_obj.last_updated = datetime.now()
    await db.update(template_obj, only=['last_updated'])
    return True


async def get_or_create_template_edit_orm(db, template_id, user_id, last_updated):
    try:
        edit = await db.get(
            TemplateEditModel, template=template_id, user=user_id
        )
        created = False
    except DoesNotExist as ex:
        edit = await db.create_or_get(
            TemplateEditModel, template=template_id, user=user_id, original_update_date=last_updated,
            date_start=datetime.now()
        )
        created = True
    return edit, created


async def get_user_edits_info_orm(db, template_id, exclude_user):
    try:
        edits = await db.execute(
            TemplateEditModel.select(TemplateEditModel, UserModel).where(
                TemplateEditModel.user_id != exclude_user,
                TemplateEditModel.template_id == template_id
            ).join(UserModel, on=(UserModel.id == TemplateEditModel.user))
        ) #TODO: check date start not empty
        result = [TemplateEditInfo.from_orm(e) for e in edits]
        return result
    except DoesNotExist as e:
        return []


async def update_user_edit_orm(db, template_id, user_id, text, headers):
    edit = await db.get(TemplateEditModel, template=template_id, user=user_id)
    edit.body_text = text
    edit.headers = headers
    edit.last_modified = datetime.now()
    await db.update(edit)
    return True
