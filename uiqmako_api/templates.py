from .models.erp_models import PoweremailTemplates
from .crud import get_template_orm, get_all_templates_orm, add_or_get_template_orm
from .schemas import Template, TemplateInfoBase


async def get_single_template(db, erp, template_id):
    template = await get_template_orm(db, template_id=template_id)
    t = PoweremailTemplates(erp, erp_id=template.erp_id, xml_id=template.xml_id)
    return Template.from_orm(t)

async def get_all_templates(db):
    templates = await get_all_templates_orm(db)
    return [TemplateInfoBase.from_orm(t) for t in templates]


async def add_template_from_xml_id(db, erp, xml_id):
    erp_template = PoweremailTemplates(erp, xml_id=xml_id) #TODO: if it doesn't exist
    template_info = None
    if erp_template:
        created, template_info = await add_or_get_template_orm(db, name=erp_template.name, xml_id=xml_id, erp_id=erp_template.id)
    return created, TemplateInfoBase.from_orm(template_info) #TODO: if different template
