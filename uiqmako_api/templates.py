import re
import json
from .models.erp_models import PoweremailTemplates
from .crud import (
    get_template_orm,
    get_all_templates_orm,
    add_or_get_template_orm,
    set_last_updated,
    get_or_create_template_edit_orm,
    get_user_edits_info_orm,
    update_user_edit_orm,
)
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
    python_reg = "(<%)(.\\s)*[^%>]*(%>)|([^\\S\n]*[^\\S]%[^>].*)"
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


async def get_or_create_template_edit(db, template_id, user):
    last_updated = (await get_template_orm(db, template_id=template_id)).last_updated
    edit, created = await get_or_create_template_edit_orm(db, template_id, user.id, last_updated)
    other_edits = await get_user_edits_info_orm(db, template_id, exclude_user=user.id)
    return edit, created


async def check_other_users_edits(db, template_id, user_id):
    other_edits = await get_user_edits_info_orm(db, template_id, exclude_user=user_id)
    return other_edits


async def save_user_edit(db, template_id, user_id, edit):
    response = await update_user_edit_orm(db, template_id, user_id, edit.def_body_text, edit.headers)
    return response