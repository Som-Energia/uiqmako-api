import pytest
from httpx import AsyncClient
from datetime import datetime
import json

@pytest.mark.asyncio
class TestApi:
    async def test_root(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {'message': "I'm the UI-QMako API"}

    async def test_template_list(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user
        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/templates")
        assert response.status_code == 200
        assert response.json() == [
            {'id': 1, 'model': "res.partner",
             'name': 'Template test', 'erp_id': None,
             'xml_id': 'template_module.template_01', 'last_updated': '2021-01-01T00:00:00'},
            {'id': 2, 'model': "res.partner",
             'name': 'Template2 test', 'erp_id': None,
             'xml_id': 'template_module.template_02', 'last_updated': '2021-01-01T00:00:00'}
        ]
        test_app.dependency_overrides = {}

    @pytest.mark.skip("Mock return check_erp_conn")
    async def test_check_erp_conn_dependency(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/templates/1")

        assert response.status_code == 503
        assert response.text == '{"detail":"Can\'t connect to ERP"}'

    async def test_add_new_template(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user
        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.post("/templates", data={"xml_id": "module_test.xml_id"})
        assert response.status_code == 200
        assert response.json()['template']['xml_id'] == "module_test.xml_id"
        assert response.json()['created']
        test_app.dependency_overrides = {}

    async def test_add_new_template_existing(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user
        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            await ac.post("/templates", data={"xml_id": "module_test.xml_id"})
            response = await ac.post("/templates", data={"xml_id": "module_test.xml_id"})
        assert response.status_code == 200
        assert response.json()['template']['xml_id'] == "module_test.xml_id"
        assert not response.json()['created']
        test_app.dependency_overrides = {}


    @pytest.mark.skip("TO fix")
    async def test_update_template(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user

        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.put("/edits/1", headers={'Authorization': "Bearer UserAll"},
                                    data={"headers": "{'name':'TESTname'}", "def_body_text": "TEST body"})
        assert response.text == 'csa'
        assert response.status_code == 200
        assert response.json() == 'TestUser'
        test_app.dependency_overrides = {}

    async def test_login_for_access_token(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.post(
                "/token", data={"username": "no_user", "password": "not_pasword"}
            )
        assert response.text == '{"detail":"Incorrect username or password"}'
        assert response.status_code == 401

    async def test_add_new_user_existing(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.post(
                "users/", data={"username": "UserAll", "password": "not_pasword"}
            )
        assert response.text == '{"detail":"Username already in use"}'
        assert response.status_code == 409

    async def test_add_new_user_new(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.post(
                "users/", data={"username": "SuperNewUser", "password": "not_pasword"}
            )
        assert response.status_code == 200



    async def test_add_new_user_list(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user
        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get(
                "users/", headers={'Authorization': "Bearer UserAll"},
            )

        assert type(response.text) == str
        user_list = json.loads(response.text)
        assert type(user_list) == list
        assert list(user_list[0].keys()) == ['id', 'username', 'disabled', 'category']
        assert response.status_code == 200

    async def test_current_user_info(self, test_app, override_get_current_active_user):
        from uiqmako_api.api.dependencies import get_current_active_user
        test_app.dependency_overrides[get_current_active_user] = lambda: override_get_current_active_user
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get(
                "users/me", headers={'Authorization': "Bearer UserAll"},
            )
        user_info = override_get_current_active_user.__dict__
        user_info.update({
            'allowed_fields': ["content","def_subject","def_subject_es_ES", "def_subject_ca_ES", "def_bcc","html","python","lang","def_body_text","def_to","def_cc"]
        })
        assert response.text == json.dumps(user_info).replace(' ','')
