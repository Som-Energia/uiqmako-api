import pytest
from .erp_test import ERPTest
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
        # Given an id that we have not imported yet
        xml_id = 'som_test.id_test'
        db_m = test_app.db_manager
        number_templates_pre = await db_m.count(TemplateInfoModel.select())

        # When we import it
        created, template = await add_template_from_xml_id(test_app.ERP, xml_id)

        # Then the number of registers is increased
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert created
        assert number_templates_post == number_templates_pre + 1
        # And the information is saved
        template_info = await db_m.get(TemplateInfoModel, xml_id=xml_id)
        assert template_info.xml_id == xml_id
        assert template_info.name == template.name
        assert template_info.model == 'res.partner'

    async def test_add_template_from_xml_id_already_exist(self, test_app, mocker):
        db_m = test_app.db_manager
        # Given that we already imported an id
        xml_id = 'som_test.id_test'
        await add_template_from_xml_id(test_app.ERP, xml_id)
        number_templates_pre = await db_m.count(TemplateInfoModel.select())

        # When we import it twice
        created, template = await add_template_from_xml_id(test_app.ERP, xml_id)

        # Then no register is added
        number_templates_post = await db_m.count(TemplateInfoModel.select())
        assert number_templates_post == number_templates_pre
        assert not created
        # And the info is updated
        template_info = await db_m.get(TemplateInfoModel, xml_id=xml_id)
        assert template_info.xml_id == xml_id
        assert template_info.name == template.name
        assert template_info.model == 'res.partner'

    @pytest.mark.parametrize(
        "body_text,split", [ pytest.param(*x[1:], id=x[0]) for x in [
            ('python', ONLY_PYTHON, [('python', ONLY_PYTHON)]),
            ('html', ONLY_HTML, [('html', ONLY_HTML.strip())]),
            ('python_html', ONLY_PYTHON+"\n"+ONLY_HTML, [
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.strip())
            ]),
            ('html_python', ONLY_HTML + "\n" + ONLY_PYTHON, [
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON)
            ]),
            ('html_python_python', ONLY_HTML + "\n" + ONLY_PYTHON + "\n" + ONLY_PYTHON, [
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON),
                ('python', ONLY_PYTHON),
            ]),
            ('python_python_html', "\n" + ONLY_PYTHON + "\n" + ONLY_PYTHON + ONLY_HTML, [
                ('python', ONLY_PYTHON),
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.strip()),
            ]),
            ('python_html_python', "\n" + ONLY_PYTHON + ONLY_HTML + ONLY_PYTHON, [
                ('python', ONLY_PYTHON),
                ('html', ONLY_HTML.replace('\n', '')),
                ('python', ONLY_PYTHON),
            ]),
        ]]
    )
    def test_parse_body_by_language(self, body_text, split):
        assert parse_body_by_language(body_text) == split

    async def test_create_template_case_ok(self, test_app):
        template_id = 1
        pre = await get_template_cases(template_id)
        result = await create_template_case(DB_MANAGER, template_id, 'test_case', 3)
        post = await get_template_cases(template_id)
        assert len(pre) + 1 == len(post)
        assert result

    async def test_create_template_case_repeated_name(self, test_app):
        template_id = 1
        pre = await get_template_cases(template_id)
        await create_template_case(DB_MANAGER, template_id, 'repeat_case', 3)
        with pytest.raises(UIQMakoBaseException):
            result = await create_template_case(DB_MANAGER, template_id, 'repeat_case', 3)
        post = await get_template_cases(template_id)
        assert len(pre) + 1 == len(post)


