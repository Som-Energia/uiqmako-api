import pytest
from .erp_test import PoweremailTemplatesTest
from uiqmako_api.utils.templates import add_template_from_xml_id, parse_body_by_language
from uiqmako_api.models.templates import TemplateInfoModel


ONLY_HTML = """
<!doctype html>
    <p>Som Energia, SCCL</p>
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


