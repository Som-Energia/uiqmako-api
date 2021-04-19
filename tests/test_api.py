import pytest
from httpx import AsyncClient
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
        assert response.json() == [{'model': "poweremail.templates", 'name': 'Template test', 'template_id': None, 'xml_id': 'template_module.template_01'},
                                   {'model': "poweremail.templates", 'name': 'Template2 test', 'template_id': None, 'xml_id': 'template_module.template_02'}]

    async def test_check_erp_conn_dependency(self, test_app):
        async with AsyncClient(app=test_app, base_url="http://test") as ac:
            response = await ac.get("/templates/1")

        assert response.status_code == 503
        assert response.text == '{"detail":"Can\'t connect to ERP"}'