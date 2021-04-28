from uiqmako_api.schemas import TemplateInfoBase
from pydantic import ValidationError
import pytest

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
