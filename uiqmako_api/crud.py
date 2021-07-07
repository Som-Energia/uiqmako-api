from datetime import datetime
from .schemas import *
from peewee_async import Manager
from .models.models import TemplateInfoModel, TemplateEditModel, CaseModel
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


async def add_or_get_template_orm(db, name, xml_id, model, erp_id=None):
    created = False
    template_info = await get_template_orm(db, xml_id=xml_id)
    if not template_info and erp_id:
        template_info = await get_template_orm(db, erp_id=erp_id)
    if not template_info and name:
        template_info = await get_template_orm(db, name=name)
    if not template_info:
        template_info, created = await db.create_or_get(
            TemplateInfoModel,
            name=name, model=model, xml_id=xml_id, erp_id=erp_id
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
        edit, created = await db.create_or_get(
            TemplateEditModel, template=template_id, user=user_id, original_update_date=last_updated,
            date_start=datetime.now()
        )
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


async def get_template_cases_orm(db, template_id):
    try:
        cases = await db.execute(CaseModel.select().where(CaseModel.template == template_id))
        result = [CaseBase.from_orm(c) for c in cases]
        return result
    except DoesNotExist:
        return []


async def get_edit_orm(db, edit_id):
    edit = await db.execute(
        TemplateEditModel.select(TemplateEditModel, TemplateInfoModel).where(
            TemplateEditModel.id == edit_id
        ).join(TemplateInfoModel, on=(TemplateInfoModel.id == TemplateEditModel.template)))
    instances = [e for e in edit]
    return instances[0] if instances else False

async def delete_edit_orm(db, edit_id):
    edit = await get_edit_orm(db, edit_id)
    return await db.delete(edit)


async def get_case_orm(db, case_id=None, case_erp_id=None, name=None, template_id=None):
    search_fields = {}
    if case_id:
        search_fields.update({'id': case_id})
    if case_erp_id:
        search_fields.update({'case_erp_id': case_erp_id})
    if name:
        search_fields.update({'name': name})
    if template_id:
        search_fields.update({'template_id': template_id})
    try:
        case = await db.get(CaseModel, **search_fields)
        return CaseBase.from_orm(case)
    except DoesNotExist as ex:
        return False

async def get_or_create_template_case_orm(db, template_id, case_name, case_id):
    case, created = await db.create_or_get(
        CaseModel,
        name=case_name, case_erp_id=int(case_id), template=template_id
    )
    return case, created
