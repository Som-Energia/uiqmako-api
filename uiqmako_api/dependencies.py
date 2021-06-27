from .models import get_db_manager
from .exceptions import ERPConnectionException

def get_db(): #TODO: remove
    return get_db_manager()

async def check_erp_conn():
    from .api import app
    if not app.ERP.get_erp_conn() or not app.ERP.test_connection():
        raise ERPConnectionException()
    return True
