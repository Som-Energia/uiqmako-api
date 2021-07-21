from fastapi import Request
from fastapi.responses import JSONResponse
from . import app
from . import users, edits, templates
from ..errors.exceptions import UsernameExists, UIQMakoBaseException, XmlIdNotFound

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
