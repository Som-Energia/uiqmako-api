from .models import get_db_manager

def get_db():
    return get_db_manager()