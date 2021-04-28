import pytest
from .erp_test import PoweremailTemplatesTest
from uiqmako_api.templates import add_template_from_xml_id
from uiqmako_api.models.models import TemplateInfoModel
from uiqmako_api.schemas import TemplateInfoBase, Template
from pytest_mock import mocker
from uiqmako_api.models.erp_models import PoweremailTemplates

@pytest.mark.asyncio
class TestTemplates:

    async def test_add_template_from_xml_id(self, test_app):
        db_m = test_app.db_manager
        number_templates_pre = await db_m.count(TemplateInfoModel.select())

        created, template = await add_template_from_xml_id(db_m, test_app.ERP, 'som_test.id_test')

        template_info = await db_m.get(TemplateInfoModel, xml_id='som_test.id_test')
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert created
        assert template_info.xml_id == 'som_test.id_test'
        assert template_info.name == template.name
        assert template_info.model == 'poweremail.templates'
        assert number_templates_post == number_templates_pre + 1

    async def test_add_template_from_xml_id_already_exist(self, test_app, mocker):
        db_m = test_app.db_manager
        number_templates_pre = await db_m.count(TemplateInfoModel.select())
        mocker.patch('uiqmako_api.models.erp_models.PoweremailTemplates')
        mocker.spec = PoweremailTemplatesTest

        created, template = await add_template_from_xml_id(db_m, test_app.ERP, 'som_test.id_test')

        template_info = await db_m.get(TemplateInfoModel, xml_id='som_test.id_test')
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert not created
        assert template_info.xml_id == 'som_test.id_test'
        assert template_info.name == template.name
        assert template_info.model == 'poweremail.templates'
        assert number_templates_post == number_templates_pre

