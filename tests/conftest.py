# import pytest
# import requests
#
# @pytest.fixture(autouse=True)
# def disable_network_calls(monkeypatch):
#     def stunted_get():
#         raise RuntimeError("Network access not allowed during testing!")
#     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
import pytest
from starlette.testclient import TestClient
from uiqmako_api.app import build_app

from uiqmako_api.models import setup_database
import shutil, os

from uiqmako_api.schemas.users import UserCategory


def create_demo_data(db_manager):
    db_manager.database.set_allow_sync(True)
    from uiqmako_api.models import templates, users
    templates.TemplateInfoModel.create(name="Template test", model="poweremail.templates", xml_id="template_module.template_01")
    templates.TemplateInfoModel.create(name="Template2 test", model="poweremail.templates", xml_id="template_module.template_02")
    users.UserModel.create(username="UserAll", hashed_pwd="hashed_pwd", disabled=False, category=UserCategory.ADMIN)
    db_manager.database.set_allow_sync(False)


def git_create_file_with_content(test_repo):
    from config import settings
    with open(os.path.join(settings.TEMPLATE_REPO_PATH, 'existing_file.mako'), 'w') as f:
        f.write("Existing file")
    test_repo.index.add('existing_file.mako')
    test_repo.index.commit("First commit")

@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
def test_app():
    from uiqmako_api.models import drop_database
    from .erp_test import ERPTest
    drop_database()
    from uiqmako_api.api.api import app
    create_demo_data(app.db_manager)
    git_create_file_with_content(app.template_repo)
    app.ERP = ERPTest()
    yield app
    drop_database()



@pytest.fixture()
async def override_get_current_active_user():
    from uiqmako_api.schemas.users import User
    return User(id=1, username='admin', category=UserCategory.ADMIN, disabled=False)


