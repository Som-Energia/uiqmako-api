from uiqmako_api.models.edits import (
    delete_edit_orm,
    delete_user_edit_orm,
    get_edit_orm,
    get_or_create_template_edit_orm,
    get_user_edits_info_orm,
    update_user_edit_orm,
)
from uiqmako_api.models.templates import (
    get_case_orm,
    get_template_orm,
)


async def get_or_create_template_edit(db, template_id, user):
    last_updated = (await get_template_orm(db, template_id=template_id)).last_updated
    edit, created = await get_or_create_template_edit_orm(db, template_id, user.id, last_updated)
    return edit, created


async def check_other_users_edits(db, template_id, user_id):
    other_edits = await get_user_edits_info_orm(db, template_id, exclude_user=user_id)
    return other_edits


async def save_user_edit(db, template_id, user_id, edit):
    response = await update_user_edit_orm(db, template_id, user_id, edit.def_body_text, edit.headers)
    return response


async def delete_user_edit(db, template_id, user_id):
    response = await delete_user_edit_orm(db, template_id, user_id)
    return response


async def render_edit(db, erp, edit_id, case_id):
    edit = await get_edit_orm(db, edit_id)
    case = await get_case_orm(db, case_id=case_id)
    if edit and case:
        if case.case_xml_id:
            model, object_id = erp.get_model_id(case.case_xml_id)
            if model != edit.template.model:
                raise Exception("Incoherent model ") #TODO: choose exception
        elif case.case_erp_id:
            object_id = case.case_erp_id
        if not object_id:
            raise Exception("No case found") #TODO: choose exception
        result = await erp.render_erp_text(edit.body_text, edit.template.model, object_id)
        return result
    else:
        return ''


async def delete_edit(db, edit_id):
    return await delete_edit_orm(db, edit_id)


async def upload_edit(db, erp, edit_id, delete_current_edit=True):
    edit = await get_edit_orm(db, edit_id)
    upload_result = await erp.upload_edit(edit.body_text, edit.headers, edit.template.xml_id)
    if upload_result:
        if delete_current_edit:
            _ = await delete_edit_orm(db, edit_id)
        return edit.template.id
    return False
