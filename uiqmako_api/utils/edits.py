from uiqmako_api.errors.exceptions import InvalidId, OutdatedEdit
from uiqmako_api.models.edits import (
    delete_edit_orm,
    delete_user_edit_orm,
    get_edit_orm,
    get_or_create_template_edit_orm,
    get_user_edits_info_orm,
    update_user_edit_orm,
)
from uiqmako_api.utils.erp_service import ErpService
from uiqmako_api.models.templates import (
    get_case_orm,
    get_template_orm,
)


async def get_or_create_template_edit(template_id, user):
    last_updated = (await get_template_orm(template_id=template_id)).last_updated
    edit, created = await get_or_create_template_edit_orm(template_id, user.id, last_updated)
    return edit, created


async def check_other_users_edits(template_id, user_id):
    other_edits = await get_user_edits_info_orm(template_id, exclude_user=user_id)
    return other_edits


async def save_user_edit(template_id, user_id, edit):
    response = await update_user_edit_orm(template_id, user_id, edit.def_body_text, edit.headers)
    return response


async def delete_user_edit(template_id, user_id):
    response = await delete_user_edit_orm(template_id, user_id)
    return response


async def render_edit(erp, edit_id, case_id):
    edit = await get_edit_orm(edit_id)
    if not edit: return ''

    case = await get_case_orm(case_id=case_id)
    if not case: return ''

    return erp.service().render_template(
        header=edit.header,
        text=edit.body_text,
        model=edit.template.model,
        id=case.case_xml_id or case.case_erp_id,
    )

async def delete_edit(edit_id):
    return await delete_edit_orm(edit_id)


async def upload_edit(erp, edit_id, delete_current_edit=True):
    edit = await get_edit_orm(edit_id)
    if not edit:
        raise Exception(f"Not such edition {edit_id}")
    template_info = await get_template_orm(template_id=edit.template.id)
    if template_info.last_updated != edit.original_update_date:
        raise OutdatedEdit("Edit from an outdated template version")
    await erp.upload_edit(
        headers=edit.headers,
        body_text=edit.body_text,
        template_xml_id=edit.template.xml_id,
    )
    if delete_current_edit:
        await delete_edit_orm(edit_id)
    return edit.template.id
