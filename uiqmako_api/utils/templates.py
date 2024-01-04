import re
from uiqmako_api.errors.exceptions import UIQMakoBaseException
from uiqmako_api.models.templates import (
    get_template_orm,
    get_all_templates_orm,
    add_or_get_template_orm,
    set_last_updated,
    get_template_cases_orm,
    get_case_orm,
    get_or_create_template_case_orm,
    delete_template_case_orm,
    delete_template_orm
)
from uiqmako_api.schemas.templates import Template, TemplateInfoBase
from uiqmako_api.utils.git import create_or_update_template


async def get_single_template(erp, git_repo, template_id, user_name=""):
    template = await get_template_orm(template_id=template_id)
    erp_template = await erp.service().load_template(template.xml_id or template.erp_id)
    has_changes = await create_or_update_template(template.xml_id, erp_template, git_repo, user_name)

    if has_changes or not template.last_updated:
        await set_last_updated(template_id=template_id)

    return erp_template


async def get_all_templates():
    templates = await get_all_templates_orm()
    return [TemplateInfoBase.from_orm(t) for t in templates]


async def add_template_from_xml_id(erp, xml_id):
    erp_template = await erp.service().load_template(xml_id)
    created, template_info = await add_or_get_template_orm(
        xml_id=xml_id,
        erp_id=erp_template.id,
        name=erp_template.name,
        model=erp_template.model_int_name,
        from_server=erp._name,
    )
    return created, TemplateInfoBase.from_orm(template_info)


def parse_body_by_language(full_text):
    """
    Function to split mako template text by language
    :param full_text: mako template text
    :return: a list of tuples, where the first element is 'python' or 'html' and the second element is a fragment of
    full_text written in said language
    """
    #python_reg = "(<%)(.)*[^%>]*(%>)|([^\\S\n]*[^\\S]%[^>][\\S ]*)"
    #python_reg = "(<%)[.\\s]*[^%>]*(%>)|(^[\\s]*%[^>][\\S ]*)"
    python_reg = "((<%(?!def))[\s\S]*?(%>))|((^[\s]*%[^>][\S ]*))|((<%def)[\S ]*?(>))|</%def>"
    rex = re.compile(python_reg, re.MULTILINE)
    parts = []
    current_pos = 0
    for match in rex.finditer(full_text):
        start = match.start()
        if start != current_pos:
            html_text = full_text[current_pos:match.start()].strip()
            if html_text:
                parts.append(('html', html_text.replace('\n','')))
        parts.append(('python', match.group()))
        current_pos = match.end()
    if current_pos != len(full_text) or not parts:
        html_text = full_text[current_pos:].strip()
        if html_text:
            parts.append(('html', html_text))
    return parts


async def get_template_cases(template_id):
    cases = await get_template_cases_orm(template_id)
    return cases


async def create_template_case(db, template_id, case_name, erp_case_id):
    case_same_name = await get_case_orm(name=case_name, template_id=template_id)
    if case_same_name:
        raise UIQMakoBaseException("Existing name case for template")
    case, created = await get_or_create_template_case_orm(template_id, case_name, erp_case_id)
    return created


async def delete_template_case(db, case_id):
    case_same_name = await get_case_orm(case_id=case_id)
    if not case_same_name:
        raise UIQMakoBaseException("Not existing name case for template")
    deleted = await delete_template_case_orm(case_id)
    return deleted

async def delete_single_template(db, template_id):
    return await delete_template_orm(template_id)
