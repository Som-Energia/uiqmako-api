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

def create_demo_data():
    from uiqmako_api.models import models
    models.TemplateInfoModel.create(name="Template test", model="poweremail.templates", xml_id="template_module.template_01")
    models.TemplateInfoModel.create(name="Template2 test", model="poweremail.templates", xml_id="template_module.template_02")


@pytest.fixture(scope='module')
def test_app():
    from uiqmako_api.api import app
    create_demo_data()
    yield app
    from uiqmako_api.models import drop_database
    drop_database()
