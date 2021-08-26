from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from . import app
from . import users, edits, templates
from .dependencies import get_current_active_user
from ..errors.exceptions import UsernameExists, UIQMakoBaseException, XmlIdNotFound
from ..errors.http_exceptions import LoginException
from ..schemas.templates import SourceInfo
from ..schemas.users import TokenInPost
from ..utils.users import authenticate_user, return_access_token

app.include_router(users.router)
app.include_router(edits.router)
app.include_router(templates.router)


@app.exception_handler(UIQMakoBaseException)
async def username_exists_handler(request: Request, exc: UIQMakoBaseException):
    _status_codes = {
        UsernameExists: 409,
        XmlIdNotFound: 404,
    }
    return JSONResponse(
        status_code=_status_codes.get(type(exc), 500),
        content={"detail": exc.msg},
    )


@app.exception_handler(Exception)
async def username_exists_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected error"},
    )


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}


@app.post("/token", response_model=TokenInPost)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise LoginException()
    return await return_access_token(user)


@app.get("/sources", dependencies=[Depends(get_current_active_user)])
async def get_sources():
    from .api import app
    sources = [
        SourceInfo(name=source._name, uri=source._uri)
        for k, source in app.ERP_DICT.items()
    ]
    return {'sources': sources}