from fastapi import APIRouter, Depends, Form
from peewee_async import Manager
from uiqmako_api.schemas.users import User
from .dependencies import get_db, check_erp_conn, get_current_active_user
from uiqmako_api.utils.edits import check_other_users_edits
from uiqmako_api.utils.templates import *
from uiqmako_api.schemas.templates import SourceInfo


router = APIRouter(
    prefix='/templates',
    tags=['templates'],
)


@router.get("")
async def templates_list(db: Manager = Depends(get_db)):
    templates = await get_all_templates(db)
    templates.sort(key=lambda x: x.name)
    return templates


@router.get("/{template_id}", dependencies=[Depends(check_erp_conn)])
async def get_template(
        template_id: int,
        db: Manager = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    if current_user:
        from . import app
        template = await get_single_template(db, app.ERP, app.template_repo, template_id)
        template_data = {
            'text': template.body_text(),
            'meta_data': template.meta_data(),
            'headers': template.headers()
        }
        return template_data


@router.post("", dependencies=[Depends(check_erp_conn)])
async def add_new_template(xml_id: str = Form(..., regex=".+\..+"), db: Manager = Depends(get_db)):
    from .api import app
    created, template_info = await add_template_from_xml_id(db, app.ERP, xml_id)
    response = {'conflict': False, "created": created, "template": template_info}
    if not created and template_info.xml_id != xml_id:
        response['conflict'] = True
    return response


@router.get("/{template_id}/checkEdits")
async def check_edits(template_id: int, current_user: User = Depends(get_current_active_user)):
    from .api import app
    check_other_edits = await check_other_users_edits(app.db_manager, template_id, current_user.id)
    return {'current_edits': check_other_edits}


@router.get("/{template_id}/cases")
async def get_cases(
        template_id: int,
        current_user: User = Depends(get_current_active_user)):
    from .api import app
    cases = await get_template_cases(app.db_manager, template_id)
    return {'cases': cases}


@router.post("/{template_id}/cases")
async def create_case(
        template_id: int,
        case_name: str = Form(...),
        case_id: str = Form(..., regex=".+\..+|[1-9][0-9]?"),
        current_user: User = Depends(get_current_active_user)):
    from .api import app
    created = await create_template_case(app.db_manager, template_id, case_name, case_id)
    return {'result': created}


@router.get("/sources")
async def get_sources(current_user: User = Depends(get_current_active_user)):
    from .api import app
    sources = [
        SourceInfo(name=source._name, uri=source._uri)
        for k, source in app.ERP_DICT.items()
    ]
    return {'sources': sources}


