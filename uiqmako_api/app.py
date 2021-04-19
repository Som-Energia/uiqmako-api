from fastapi import FastAPI
from uiqmako_api.erp_utils import ERP
from uiqmako_api.models import setup_database


def build_app():
    import config

    app = FastAPI()
    setup_database(True)
    app.settings = config.settings
    try:
        app.ERP = ERP()
    except:
        app.ERP = None
        print("Cannot connect to ERP") #TODO: use logging
    return app
