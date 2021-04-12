from fastapi import Depends, HTTPException, status
from datetime import timedelta
from .registration.schemas import Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .dependencies import get_db
from .app import build_app
from .crud import *
from .erp_utils import get_erp_template
from .registration.login import authenticate_user, create_access_token
from config import settings

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


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Manager = Depends(get_db)):
    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
