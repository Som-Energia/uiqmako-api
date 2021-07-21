import re

from uiqmako_api.errors.exceptions import UIQMakoBaseException
from uiqmako_api.models.erp_models import PoweremailTemplates
from uiqmako_api.models.templates import (
    get_template_orm,
    get_all_templates_orm,
    add_or_get_template_orm,
    set_last_updated,
    get_template_cases_orm,
    get_case_orm,
    get_or_create_template_case_orm,
)
from uiqmako_api.schemas.templates import Template, TemplateInfoBase
from uiqmako_api.utils.git import create_or_update_template


async def get_single_template(db, erp, git_repo, template_id):
    template = await get_template_orm(db, template_id=template_id)
    t = PoweremailTemplates(erp, erp_id=template.erp_id, xml_id=template.xml_id)
    has_changes = await create_or_update_template(template.xml_id, Template.from_orm(t), git_repo)
    if has_changes:
        await set_last_updated(db, template_id=template_id)
    return Template.from_orm(t)


async def get_all_templates(db):
    templates = await get_all_templates_orm(db)
    return [TemplateInfoBase.from_orm(t) for t in templates]


async def add_template_from_xml_id(db, erp, xml_id):
    erp_template = PoweremailTemplates(erp, xml_id=xml_id)
    template_info = None
    if erp_template:
        created, template_info = await add_or_get_template_orm(
            db, name=erp_template.name,
            xml_id=xml_id,
            model=erp_template.model_int_name,
            erp_id=erp_template.id,
        )
    return created, TemplateInfoBase.from_orm(template_info) #TODO: if different template


def parse_body_by_language(full_text):
    python_reg = "(<%)(.)*[^%>]*(%>)|([^\\S\n]*[^\\S]%[^>][\\S ]*)"
    rex = re.compile(python_reg, re.DOTALL)
    parts = []
    current_pos = 0
    for match in rex.finditer(full_text):
        start = match.start()
        if start != current_pos:
            html_text = full_text[current_pos:match.start()].strip()
            if html_text:
                parts.append(('html', html_text.replace('\n','').replace("<b>",'<strong>').replace('</b>', '</strong>')))
        parts.append(('python', match.group()))
        current_pos = match.end()
    if current_pos != len(full_text) or not parts:
        html_text = full_text[current_pos:].strip()
        if html_text:
            parts.append(('html', html_text))
    return parts


async def get_template_cases(db, template_id):
    cases = await get_template_cases_orm(db, template_id)
    return cases


async def create_template_case(db, template_id, case_name, case_id):
    #TODO: Check id semàntic
    case_same_name = await get_case_orm(db, template_id=template_id, name=case_name)
    if case_same_name:
        raise UIQMakoBaseException("Existing name case for template")
    case, created = await get_or_create_template_case_orm(db, template_id, case_name, case_id)
    return created
