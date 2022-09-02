from uiqmako_api.schemas.templates import TemplateInfoBase, Template
from uiqmako_api.schemas.edits import RawEdit
from uiqmako_api.schemas.users import User, UserCategory
from .erp_test import ERPTest
from pydantic import ValidationError
import pytest, json

@pytest.mark.parametrize("invalid_xml_id", [
    "without_module",
    ".empty_module",
    "empty_name."
])
def test__xml_id_validator__validationError(invalid_xml_id):
    with pytest.raises(ValidationError):
        TemplateInfoBase(id=1, name='test', model='account.account', xml_id=invalid_xml_id)

@pytest.mark.parametrize("valid_xml_id", [
    "with.module",
    None,
])
def test__xml_id_validator__ok(valid_xml_id):
    TemplateInfoBase(id=3, name='test', model='account.account', xml_id=valid_xml_id)


PYTHON_PART = ('python', '<%\nfor a in [1,2]:\n\tprint(a)\n%>')
PYTHON_INLINE = ('python', ' % if a:')
HTML_PART =('html', '<p>text</p><p><b>Bold text</b></p>')
PRETTY_HTML = '<p>\n text\n</p>\n<p>\n <b>\n  Bold text\n </b>\n</p>\n'
@pytest.mark.parametrize(
    "input,expected", [ pytest.param(*x[1:], id=x[0]) for x in [
    ('empty', [], "full text"),
    ('python', [PYTHON_PART], PYTHON_PART[1]+'\n'),
    ('html', [HTML_PART], PRETTY_HTML),
    ('python_html',[PYTHON_PART, HTML_PART], PYTHON_PART[1]+'\n' + PRETTY_HTML),
    ('python_html_inline_python',
        [PYTHON_PART, HTML_PART, PYTHON_INLINE, HTML_PART],
        PYTHON_PART[1] + '\n' + PRETTY_HTML + PYTHON_INLINE[1] + '\n' + PRETTY_HTML
    ),
]])
def test_compose_text_types(input, expected):
    re = RawEdit(by_type=json.dumps(input), headers ='{"def_to:""}', def_body_text="full text")
    assert re.def_body_text == expected
    assert re.headers == '{"def_to:""}'


@pytest.mark.asyncio
async def test_template_schema():
    template = await ERPTest().service().load_template('module.id')
    assert template.def_body_text == 'def_body_text_module.id'
    assert set(template.headers().keys()) == set([
        'def_subject', 'def_subject_es_ES', 'def_subject_ca_ES',
        'def_to', 'def_cc', 'def_bcc', 'lang',
    ])
    assert set(template.meta_data().keys()) == set(['name', 'model_int_name', 'id'])
    assert template.body_text() == {
        'def_body_text': 'def_body_text_module.id',
        'by_type': [('html', 'def_body_text_module.id')],
    }


BASIC_ALLOWED = ['content', 'def_subject', 'def_subject_es_ES', 'def_subject_ca_ES', 'def_bcc', 'html']
PYTHON_ALLOWED = BASIC_ALLOWED + ['python', 'lang', 'def_body_text', 'def_to', 'def_cc']
@pytest.mark.parametrize("category,expected", [
    (UserCategory.ADMIN, PYTHON_ALLOWED),
    (UserCategory.PYTHON_USER, PYTHON_ALLOWED),
    (UserCategory.BASIC_USER, BASIC_ALLOWED),

])
def test_user_schema(category, expected):
    user = User(id=1, username='usr', disabled=False, category=category)
    user_disabled = User(id=2, username='usr', disabled=True, category=category)
    assert user.get_allowed_fields() == expected
    assert user_disabled.get_allowed_fields() == []
