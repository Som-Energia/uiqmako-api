from fastapi import Depends, Form, Request
from pydantic.typing import List, Tuple
from peewee_async import Manager
from datetime import timedelta, datetime
from .registration.schemas import Token, User, UserInPost
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .dependencies import get_db, check_erp_conn
from .app import build_app
from .templates import *
from .registration.login import authenticate_user, create_access_token
from config import settings
from .exceptions import LoginException
from .schemas import RawEdit, SourceInfo
from .registration.login import get_current_active_user, add_user, return_acces_token, check_current_active_user_is_admin, update_user
from .models.login import get_users_list
from .exceptions import UnexpectedError

app = build_app()


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}


@app.get("/templates")
async def templates_list(db: Manager = Depends(get_db)):
    templates = await get_all_templates(app.db_manager)
    return templates


@app.get("/templates/{template_id}", dependencies=[Depends(check_erp_conn)])
async def get_template(template_id: int, db: Manager = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user:
        template = await get_single_template(db, app.ERP, app.template_repo, template_id)
        template_data = {
            'text': template.body_text(),
            'meta_data': template.meta_data(),
            'headers': template.headers()
        }
        return template_data


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Manager = Depends(get_db)):
    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise LoginException()
    return await return_acces_token(user)

@app.post("/users")
async def add_new_user(username: str = Form(...), password: str = Form(...), db: Manager = Depends(get_db)):
    user = await add_user(username, password, db)
    token = await return_acces_token(user)
    return token

@app.get("/users")
async def get_users(is_admin: User = Depends(check_current_active_user_is_admin), db: Manager = Depends(get_db)):
    user_list = list(filter(lambda x: x.username != 'admin', (await get_users_list(db))))
    user_list.sort(key=lambda x: x.username)
    return user_list

@app.post("/templates", dependencies=[Depends(check_erp_conn)])
async def add_new_template(xml_id: str = Form(..., regex=".+\..+"), db: Manager = Depends(get_db)):
    created, template_info = await add_template_from_xml_id(db, app.ERP, xml_id)
    response = {'conflict': False, "created": created, "template": template_info}
    if not created and template_info.xml_id != xml_id:
        response['conflict'] = True
    return response

@app.post("/checkEdits/{template_id}")
async def check_edits(template_id: int, current_user: User = Depends(get_current_active_user)):
    check_other_edits = await check_other_users_edits(app.db_manager, template_id, current_user.id)
    return {'current_edits': check_other_edits}


@app.post("/edit/{template_id}")
async def start_edit(template_id: int, current_user: User = Depends(get_current_active_user)):
    edit, created = await get_or_create_template_edit(app.db_manager, template_id, current_user)
    template = await get_single_template(app.db_manager, app.ERP, app.template_repo, template_id)
    allowed_fields_modify = current_user.get_allowed_fields()
    edit_data = {'meta_data': template.meta_data(), 'allowed_fields': allowed_fields_modify, 'edit_id': edit.id}
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

@app.put("/edit/{template_id}")
async def update_edit(
        template_id: int,
        body: RawEdit,
        current_user: User = Depends(get_current_active_user)):
    response = await save_user_edit(app.db_manager, template_id, current_user.id, body)
    return {'result': response}

@app.get("/cases/{template_id}")
async def get_cases(
        template_id: int,
        current_user: User = Depends(get_current_active_user)):
    cases = await get_template_cases(app.db_manager, template_id)
    return {'cases': cases}

@app.post("/cases/{template_id}")
async def create_case(
        template_id: int,
        case_name: str = Form(...),
        case_id: str = Form(..., regex=".+\..+|[1-9][0-9]?"),
        current_user: User = Depends(get_current_active_user)):
    created = await create_template_case(app.db_manager, template_id, case_name, case_id)
    return {'result': created}

@app.get("/render/{edit_id}", dependencies=[Depends(check_erp_conn)])
async def render_template(edit_id: int, case_id: int,
        current_user: User = Depends(get_current_active_user)):
    result = await render_edit(app.db_manager, app.ERP, edit_id, case_id)
    return result

@app.get("/sources")
async def get_sources(current_user: User = Depends(get_current_active_user)):

    sources = [
        SourceInfo(name=source._name, uri=source._uri)
        for k, source in app.ERP_DICT.items()
    ]
    return {'sources': sources}

@app.post("/upload/{edit_id}", dependencies=[Depends(check_erp_conn)])
async def upload_to_erp(edit_id: int, source: str, current_user: User = Depends(get_current_active_user)):

    delete_current_edit = False
    if source == app.ERP._name:
        delete_current_edit = True
    updated_template_id = await upload_edit(app.db_manager, app.ERP, edit_id, delete_current_edit)
    if updated_template_id:
        if source == app.ERP._name:
            updated_template = await get_single_template(app.db_manager, app.ERP, app.template_repo, updated_template_id)
        return updated_template_id
    raise UnexpectedError


@app.put("/users")
async def update_users(
    userdata: UserInPost,
    is_admin: User = Depends(check_current_active_user_is_admin),
    db: Manager = Depends(get_db)):
    result = await update_user(userdata, db)
    return result
