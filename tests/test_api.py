import pytest
from httpx import AsyncClient
from uiqmako_api.models.login import UserModel
@pytest.mark.asyncio
class TestApi:

    async def test_root(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {'message': "I'm the UI-QMako API"}

    async def test_template_list(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/templates")
        assert response.status_code == 200
        assert response.json() == [{'id': 1, 'model': "poweremail.templates", 'name': 'Template test', 'erp_id': None, 'xml_id': 'template_module.template_01'},
                                   {'id': 2, 'model': "poweremail.templates", 'name': 'Template2 test', 'erp_id': None, 'xml_id': 'template_module.template_02'}]

    @pytest.mark.skip("Mock return check_erp_conn")
    async def test_check_erp_conn_dependency(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/templates/1")

        assert response.status_code == 503
        assert response.text == '{"detail":"Can\'t connect to ERP"}'

    async def test_add_new_template(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.post("/templates", data={"xml_id": "module_test.xml_id"})
        assert response.status_code == 200
        assert response.json()['template']['xml_id'] == "module_test.xml_id"
        assert response.json()['created']