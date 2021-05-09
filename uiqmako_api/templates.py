import re
from .models.erp_models import PoweremailTemplates
from .crud import get_template_orm, get_all_templates_orm, add_or_get_template_orm, set_last_updated
from .schemas import Template, TemplateInfoBase
from .git_utils import create_or_update_template


async def get_single_template(db, erp, git_repo, template_id):
    template = await get_template_orm(db, template_id=template_id)
    t = PoweremailTemplates(erp, erp_id=template.erp_id, xml_id=template.xml_id)
    has_changes = await create_or_update_template(template.xml_id, t, git_repo)
    if has_changes:
        await set_last_updated(db, template_id=template_id)
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

def parse_body_by_language(full_text):
    python_reg = "(<%)(.\\s)*[^%>]*(%>)"
    rex = re.compile(python_reg)
    parts = []
    current_pos = 0
    for match in rex.finditer(full_text):
        start = match.start()
        if start != current_pos:
            html_text = full_text[current_pos:match.start()].strip()
            if html_text:
                parts.append(('html', html_text))
        parts.append(('python', match.group()))
        current_pos = match.end()
    if current_pos != len(full_text) or not parts:
        html_text = full_text[current_pos:].strip()
        if html_text:
            parts.append(('html', html_text))
    return parts