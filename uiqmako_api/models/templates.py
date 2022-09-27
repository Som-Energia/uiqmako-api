import peewee
from datetime import datetime
from . import database, get_db_manager
from uiqmako_api.schemas.templates import TemplateInfoBase, CaseBase

db = get_db_manager()


class TemplateInfoModel(peewee.Model):
    id = peewee.AutoField()
    name = peewee.CharField(unique=True)
    model = peewee.CharField()
    xml_id = peewee.CharField(null=True, unique=True)
    erp_id = peewee.IntegerField(null=True, unique=True)
    last_updated = peewee.DateTimeField(null=True)

    class Meta:
        database = database
        table_name = "template_info"


class CaseModel(peewee.Model):
    id = peewee.AutoField()
    name = peewee.CharField()
    case_erp_id = peewee.IntegerField(null=True)
    case_xml_id = peewee.CharField(null=True)
    template = peewee.ForeignKeyField(TemplateInfoModel)

    class Meta:
        database = database
        table_name = "case_info"


async def get_all_templates_orm():
    templates = await db.execute(TemplateInfoModel.select())
    return templates


async def get_template_orm(template_id=None, erp_id=None, xml_id=None, name=None):
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
        template_id = await db.get(TemplateInfoModel, **search_fields)
        return TemplateInfoBase.from_orm(template_id)
    except peewee.DoesNotExist as ex:
        return None


async def add_or_get_template_orm(name, xml_id, model, erp_id=None):
    created = False
    template_info = await get_template_orm(xml_id=xml_id)
    if not template_info and erp_id:
        template_info = await get_template_orm(erp_id=erp_id)
    if not template_info and name:
        template_info = await get_template_orm(name=name)
    if not template_info:
        template_info, created = await db.create_or_get(
            TemplateInfoModel,
            name=name, model=model, xml_id=xml_id, erp_id=erp_id
        )

    return created, template_info


async def set_last_updated(template_id):
    template_obj = await db.get(TemplateInfoModel, id=template_id)
    template_obj.last_updated = datetime.now()
    await db.update(template_obj, only=['last_updated'])
    return True


async def get_template_cases_orm(template_id):
    try:
        cases = await db.execute(CaseModel.select().where(CaseModel.template == template_id))
        result = [CaseBase.from_orm(c) for c in cases]
        return result
    except peewee.DoesNotExist:
        return []


async def get_case_orm(case_id=None, case_erp_id=None, name=None, template_id=None):
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
    except peewee.DoesNotExist as ex:
        return False


async def get_or_create_template_case_orm(template_id, case_name, case_id):
    case, created = await db.create_or_get(
        CaseModel,
        name=case_name, case_erp_id=int(case_id), template=template_id
    )
    return case, created
