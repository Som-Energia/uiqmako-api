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

def create_demo_data(db_manager):
    db_manager.database.set_allow_sync(True)
    from uiqmako_api.models import models
    models.TemplateInfoModel.create(name="Template test", model="poweremail.templates", xml_id="template_module.template_01")
    models.TemplateInfoModel.create(name="Template2 test", model="poweremail.templates", xml_id="template_module.template_02")
    db_manager.database.set_allow_sync(False)


def create_file_with_content(repo_path, test_repo):
    with open(os.path.join(repo_path, 'existing_file.mako'), 'w') as f:
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
    from uiqmako_api.api import app
    from .erp_test import ERPTest
    create_demo_data(app.db_manager)
    app.ERP = ERPTest()
    yield app
    from uiqmako_api.models import drop_database
    drop_database()


@pytest.fixture(scope="module")
def test_template_repo():
    import git
    from config import settings

    if os.path.exists(settings.TEMPLATE_REPO_PATH):
        raise Exception("Path for testing git repo is already being used")

    test_repo = git.Repo.init(settings.TEMPLATE_REPO_PATH)
    create_file_with_content(settings.TEMPLATE_REPO_PATH, test_repo)
    yield test_repo
    shutil.rmtree(settings.TEMPLATE_REPO_PATH)


