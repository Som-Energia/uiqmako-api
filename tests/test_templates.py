import pytest
from .erp_test import PoweremailTemplatesTest, ERPTest
from uiqmako_api.utils.templates import *
from uiqmako_api.models.templates import TemplateInfoModel
from uiqmako_api.models import get_db_manager
from uiqmako_api.utils.git import setup_template_repository
ONLY_HTML = """
<!doctype html>
    <p>Som Energia, SCCL %</p>
    <p><a href=\"http://es.support.somenergia.coop\">Ayuda</a>
</html>
"""

ONLY_PYTHON = """<%
from mako.template import Template
text_legal = render(
    t_obj.read(
    object._cr, object._uid, [template_id], ['def_body_text']
)[0]['def_body_text'],object)
%>"""

DB_MANAGER = get_db_manager()
ERP = ERPTest()
GIT = setup_template_repository()


@pytest.mark.asyncio
class TestTemplates:

    async def test_add_template_from_xml_id(self, test_app):
        db_m = test_app.db_manager
        number_templates_pre = await db_m.count(TemplateInfoModel.select())

        created, template = await add_template_from_xml_id(test_app.ERP, 'som_test.id_test')

        template_info = await db_m.get(TemplateInfoModel, xml_id='som_test.id_test')
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert created
        assert template_info.xml_id == 'som_test.id_test'
        assert template_info.name == template.name
        assert template_info.model == 'res.partner'
        assert number_templates_post == number_templates_pre + 1

    async def test_add_template_from_xml_id_already_exist(self, test_app, mocker):
        db_m = test_app.db_manager
        number_templates_pre = await db_m.count(TemplateInfoModel.select())
        mocker.patch('uiqmako_api.models.erp_models.PoweremailTemplates')
        mocker.spec = PoweremailTemplatesTest

        created, template = await add_template_from_xml_id(test_app.ERP, 'som_test.id_test')

        template_info = await db_m.get(TemplateInfoModel, xml_id='som_test.id_test')
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert not created
        assert template_info.xml_id == 'som_test.id_test'
        assert template_info.name == template.name
        assert template_info.model == 'res.partner'
        assert number_templates_post == number_templates_pre

    @pytest.mark.parametrize(
        "body_text,split", [
            (ONLY_PYTHON, [('python', ONLY_PYTHON)]),
            (ONLY_HTML, [('html', ONLY_HTML.strip())]),
            (ONLY_PYTHON+"\n"+ONLY_HTML, [
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.strip())
            ]),
            (ONLY_HTML + "\n" + ONLY_PYTHON, [
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON)
            ]),
            (ONLY_HTML + "\n" + ONLY_PYTHON + "\n" + ONLY_PYTHON, [
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON),
                ('python', ONLY_PYTHON),
            ]),
            ("\n" + ONLY_PYTHON + "\n" + ONLY_PYTHON + ONLY_HTML, [
                ('python', ONLY_PYTHON),
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.strip()),
            ]),

            ("\n" + ONLY_PYTHON + ONLY_HTML + ONLY_PYTHON, [
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON),
            ]),

        ]
    )
    def test_parse_body_by_language(self, body_text, split):
        assert parse_body_by_language(body_text) == split

    async def test_create_template_case_ok(self):
        template_id = 1
        pre = await get_template_cases(template_id)
        result = await create_template_case(DB_MANAGER, template_id, 'test_case', 3)
        post = await get_template_cases(template_id)
        assert len(pre) + 1 == len(post)
        assert result

    async def test_create_template_case_repeated_name(self):
        template_id = 1
        pre = await get_template_cases(template_id)
        await create_template_case(DB_MANAGER, template_id, 'repeat_case', 3)
        with pytest.raises(UIQMakoBaseException):
            result = await create_template_case(DB_MANAGER, template_id, 'repeat_case', 3)
        post = await get_template_cases(template_id)
        assert len(pre) + 1 == len(post)

