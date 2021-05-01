from fastapi import Depends, Form
from peewee_async import Manager
from datetime import timedelta
from .registration.schemas import Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .dependencies import get_db, check_erp_conn
from .app import build_app
from .templates import *
from .registration.login import authenticate_user, create_access_token
from config import settings
from .exceptions import LoginException


app = build_app()


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}


@app.get("/templates")
async def templates_list(db: Manager = Depends(get_db)):
    templates = await get_all_templates(app.db_manager)
    return templates


@app.get("/templates/{template_id}", dependencies=[Depends(check_erp_conn)])
async def get_template(template_id: int, db: Manager = Depends(get_db)):
    template = await get_single_template(db, app.ERP, template_id)
    body_text_by_type = parse_body_by_language(template.def_body_text)
    return {'body_text_by_type': body_text_by_type, 'template': template}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Manager = Depends(get_db)):
    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise LoginException()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/templates", dependencies=[Depends(check_erp_conn)])
async def add_new_template(xml_id: str = Form(..., regex=".+\..+"), db: Manager = Depends(get_db)):
    created, template_info = await add_template_from_xml_id(db, app.ERP, xml_id)
    response = {'conflict': False, "created": created, "template": template_info}
    if not created and template_info.xml_id != xml_id:
        response['conflict'] = True
    return response
