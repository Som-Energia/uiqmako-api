from fastapi import Depends, APIRouter
import json
from uiqmako_api.schemas.users import User
from .dependencies import check_erp_conn, get_current_active_user
from uiqmako_api.utils.edits import *
from uiqmako_api.utils.templates import (
    get_single_template,
    parse_body_by_language,
)
from uiqmako_api.errors.http_exceptions import UnexpectedError
from uiqmako_api.schemas.edits import RawEdit
from . import app

router = APIRouter(
    prefix='/edits',
    tags=['edits'],
)


@router.post("/{template_id}", dependencies=[Depends(check_erp_conn)])
async def start_edit(template_id: int, current_user: User = Depends(get_current_active_user)):
    edit, created = await get_or_create_template_edit(template_id, current_user)
    template = await get_single_template(app.ERP, app.template_repo, template_id)
    allowed_fields_modify = current_user.get_allowed_fields()
    edit_data = {'meta_data': template.meta_data(), 'allowed_fields': allowed_fields_modify, 'edit_id': edit.id, 'created': created}
    if created or not edit.last_modified:
        edit_data['text'] = template.body_text()
        edit_data['headers'] = template.headers()
    else:
        edit_data['text'] = {
            'def_body_text': edit.body_text,
            'by_type': parse_body_by_language(edit.body_text)
        }
        edit_data['headers'] = json.loads(edit.headers)
    return edit_data


@router.put("/{template_id}")
async def update_edit(
        template_id: int,
        body: RawEdit,
        current_user: User = Depends(get_current_active_user)):
    response = await save_user_edit(template_id, current_user.id, body)
    return {'result': response}


@router.delete("/{template_id}")
async def delete_edit(
        template_id: int,
        current_user: User = Depends(get_current_active_user)):
    response = await delete_user_edit(template_id, current_user.id)
    return {'result': response}


@router.get("/{edit_id}/render", dependencies=[Depends(check_erp_conn), Depends(get_current_active_user)])
async def render_template(edit_id: int, case_id: int,):
    result = await render_edit(app.ERP, edit_id, case_id)
    return result


@router.post("/{edit_id}/upload", dependencies=[Depends(check_erp_conn)])
async def upload_to_erp(edit_id: int, source: str,  current_user: User = Depends(get_current_active_user)):
    delete_current_edit = False
    if source == app.ERP._name:
        delete_current_edit = True
    updated_template_id = await upload_edit(app.ERP_DICT[source], edit_id, delete_current_edit)
    if not updated_template_id:
        raise UnexpectedError
    if source == app.ERP._name:
        updated_template = await get_single_template(app.ERP, app.template_repo, updated_template_id, current_user.username)
    return updated_template_id
