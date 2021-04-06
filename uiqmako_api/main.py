from fastapi import Depends
from peewee_async import Manager
from .models import TemplateInfoModel
from .schemas import TemplateInfo
from .dependencies import get_db
from .app import build_app
from .crud import *
from .erp_utils import get_erp_template

app = build_app()


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}

@app.get("/templates")
async def templates_list(db: Manager = Depends(get_db)):
    templates = await get_all_templates(db)
    return templates

@app.get("/templates/{template_id}")
async def get_template(template_id: int, db: Manager = Depends(get_db)):
    template = await get_template_orm(db, template_id=template_id)
    t = get_erp_template(id=template.template_id, xml_id=template.xml_id)
    return t
