from fastapi import APIRouter, Depends, Form
from uiqmako_api.schemas.users import User
from .dependencies import check_erp_conn, get_current_active_user
from uiqmako_api.utils.edits import check_other_users_edits
from uiqmako_api.utils.templates import *

router = APIRouter(
    prefix='/templates',
    tags=['templates'],
)


@router.get("", dependencies=[Depends(get_current_active_user)])
async def templates_list():
    templates = await get_all_templates()
    templates.sort(key=lambda x: x.name)
    return templates


@router.get("/{template_id}", dependencies=[Depends(check_erp_conn), Depends(get_current_active_user)])
async def get_template(template_id: int):
    from . import app
    template = await get_single_template(app.ERP, app.template_repo, template_id)
    template_data = {
        'text': template.body_text(),
        'meta_data': template.meta_data(),
        'headers': template.headers()
    }
    return template_data


@router.post("", dependencies=[Depends(check_erp_conn), Depends(get_current_active_user)])
async def add_new_template(xml_id: str = Form(..., regex=".+\..+")):
    from .api import app
    created, template_info = await add_template_from_xml_id(app.ERP, xml_id)
    response = {'conflict': False, "created": created, "template": template_info}
    if not created and template_info.xml_id != xml_id:
        response['conflict'] = True
    return response


@router.get("/{template_id}/checkEdits")
async def check_edits(template_id: int, current_user: User = Depends(get_current_active_user)):
    from .api import app
    check_other_edits = await check_other_users_edits(template_id, current_user.id)
    return {'current_edits': check_other_edits}


@router.get("/{template_id}/cases", dependencies=[Depends(get_current_active_user)])
async def get_cases(template_id: int):
    cases = await get_template_cases(template_id)
    return {'cases': cases}


@router.post("/{template_id}/cases", dependencies=[Depends(get_current_active_user)])
async def create_case(
        template_id: int,
        case_name: str = Form(...),
        case_id: str = Form(..., regex=".+\..+|[1-9][0-9]?")):
    from .api import app
    created = await create_template_case(
        app.db_manager,
        template_id,
        case_name,
        erp_case_id=case_id
    )
    return {'result': created}


@router.delete("/{template_id}/cases/{case_id}", dependencies=[Depends(get_current_active_user)])
async def delete_case(case_id: int):
    from .api import app
    deleted = await delete_template_case(app.db_manager, case_id)
    return {'result': deleted}


@router.get("/importable/{source}", dependencies=[Depends(get_current_active_user)])
async def importable_template_list(source: str):
    from . import app
    app.ERP = app.ERP_DICT[source]

    templates = await app.ERP.service().template_list()
    return {'templates': templates}
