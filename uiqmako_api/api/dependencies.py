from uiqmako_api.models import get_db_manager
from uiqmako_api.errors.exceptions import ERPConnectionException


def get_db(): #TODO: remove
    return get_db_manager()


async def check_erp_conn():
    from .api import app
    if not app.ERP.get_erp_conn() or not app.ERP.test_connection():
        raise ERPConnectionException()
    return True
