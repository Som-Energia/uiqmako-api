from fastapi import Depends
from peewee_async import Manager
from .models import TemplateInfoModel
from .schemas import TemplateInfo
from .dependencies import get_db
from .app import build_app
from .crud import *

app = build_app()


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}

@app.get("/templates")
async def templates_list(db: Manager = Depends(get_db)):
    templates = await get_all_templates(db)
    return templates