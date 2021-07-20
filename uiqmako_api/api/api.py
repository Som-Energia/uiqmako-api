from . import app
from . import users, edits, templates


app.include_router(users.router)
app.include_router(edits.router)
app.include_router(templates.router)


@app.get("/")
async def root():
    return {"message": "I'm the UI-QMako API"}
