from fastapi import FastAPI
from uiqmako_api.erp_utils import ERP
from uiqmako_api.models import setup_database, get_db_manager
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]


def build_app():
    import config

    app = FastAPI()
    setup_database(True)
    app.db_manager = get_db_manager()
    app.settings = config.settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    try:
        app.ERP = ERP()
    except:
        app.ERP = None
        print("Cannot connect to ERP") #TODO: use logging
    return app
