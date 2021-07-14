from fastapi import FastAPI
from uiqmako_api.erp_utils import ERP_PROD, ERP_LOCAL, ERP_TESTING
from uiqmako_api.models import setup_database, get_db_manager
from uiqmako_api.git_utils import setup_template_repository
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
    app.template_repo = setup_template_repository()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.ERP_DICT = {}
    try:
        app.ERP = ERP_PROD()
        app.ERP_DICT[app.ERP._name] = app.ERP
    except:
        app.ERP = None
        print("Cannot connect to Prod ERP") #TODO: use logging
    try:
        app.ERP_DICT['TESTING'] = ERP_TESTING()
    except:
        app.ERP_TESTING = None
        print("Cannot connect to Test ERP") #TODO: use logging
    return app
