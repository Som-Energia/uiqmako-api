# import pytest
# import requests
#
# @pytest.fixture(autouse=True)
# def disable_network_calls(monkeypatch):
#     def stunted_get():
#         raise RuntimeError("Network access not allowed during testing!")
#     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
import pytest
from datetime import datetime
from starlette.testclient import TestClient
from uiqmako_api.app import build_app

from uiqmako_api.models import setup_database
import shutil, os

from uiqmako_api.schemas.users import UserCategory

pytest.register_assert_rewrite("tests.erp_service_testsuite")

""""
@pytest.fixture
def template_infos():

    templates = await get_all_templates_orm(db_manager)
@pytest.fixture
def template_info_2(db_manager):
    pass
"""
def create_demo_data(db_manager):
    db_manager.database.set_allow_sync(True)
    from uiqmako_api.models import templates, users, edits
    tim_1 = templates.TemplateInfoModel.create(
        name="Template test",
        model="res.partner",
        xml_id="template_module.template_01",
        last_updated=datetime(2021, 1, 1),
    )
    tim_2 = templates.TemplateInfoModel.create(
        name="Template2 test",
        model="res.partner",
        xml_id="template_module.template_02",
        last_updated=datetime(2021, 1, 1),
    )
    u_1 = users.UserModel.create(
        username="UserAll",
        hashed_pwd="hashed_pwd",
        disabled=False,
        category=UserCategory.ADMIN,
    )
    u_2 = users.UserModel.create(
        username="UserBasic",
        hashed_pwd="hashed_pwd",
        disabled=False,
        category=UserCategory.BASIC_USER,
    )
    e_1 = edits.TemplateEditModel.create(
        template_id=tim_1.id,
        user_id=u_1.id,
        original_update_date=datetime.now(),
        date_start=datetime.now(),
    )
    db_manager.database.set_allow_sync(True)


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

@pytest.fixture
def database():
    from uiqmako_api.api.api import app
    from uiqmako_api.models import drop_database
    try:
        drop_database()
        setup_database()
        create_demo_data(app.db_manager)
        yield
    finally:
        drop_database()

@pytest.fixture
def gitrepo():
    from uiqmako_api.api.api import app
    from uiqmako_api.utils.git import setup_template_repository
    try:
        app.template_repo = setup_template_repository()
        git_create_file_with_content(app.template_repo)
        yield app.template_repo
    finally:
        remove_git_repo()


@pytest.fixture
def test_app(database, gitrepo):
    from .erp_test import ERPTest
    from uiqmako_api.api.api import app
    app.ERP = ERPTest()
    yield app



@pytest.fixture()
async def override_get_current_active_user():
    from uiqmako_api.schemas.users import User
    return User(id=1, username='admin', category=UserCategory.ADMIN, disabled=False)

@pytest.fixture()
async def override_get_current_active_user_basic():
    from uiqmako_api.schemas.users import User
    return User(id=2, username='basic', category=UserCategory.BASIC_USER, disabled=False)


@pytest.fixture()
async def override_get_current_disabled_user():
    from uiqmako_api.schemas.users import User
    from uiqmako_api.api.dependencies import get_current_active_user
    return await get_current_active_user(User(id=1, username='admin', category=UserCategory.ADMIN, disabled=True))


def remove_git_repo():
    import shutil
    from config import settings
    shutil.rmtree(settings.TEMPLATE_REPO_PATH, ignore_errors=True)





