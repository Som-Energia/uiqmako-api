import unittest
from uiqmako_api.schemas import TemplateInfoBase
from pydantic import ValidationError

class TestSchemas(unittest.TestCase):

    def test__xml_id_validator__validationError(self):
        with self.assertRaises(ValidationError):
            temp_info = TemplateInfoBase(name='test', model='account.account', xml_id="without_module")
        with self.assertRaises(ValidationError):
            temp_info = TemplateInfoBase(name='test', model='account.account', xml_id=".empty_module")
        with self.assertRaises(ValidationError):
            temp_info = TemplateInfoBase(name='test', model='account.account', xml_id="empty_name.")

    def test__xml_id_validator__ok(self):
        temp_info = TemplateInfoBase(name='test', model='account.account', xml_id="with.module")
        temp_info = TemplateInfoBase(name='test', model='account.account', xml_id=None)
        self.assertTrue(True)
