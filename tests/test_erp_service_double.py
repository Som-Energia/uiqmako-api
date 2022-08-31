import pytest
from .erp_service_testsuite import (
    existing_template,
    ErpService_TestSuite,
)
from .erp_test import ErpServiceDouble

pytestmark = [
    pytest.mark.asyncio,
]

@pytest.fixture
def erp_service():
    service = ErpServiceDouble()
    service.add_dummy_template(
        xml_id = existing_template.xml_id,
        id = existing_template.erp_id,
        def_subject = "Untranslated subject",
        def_subject_es_ES = existing_template.subject_es_ES,
        def_subject_ca_ES = existing_template.subject_ca_ES,
        name = existing_template.name,
        model_int_name = existing_template.model,
    )
    return service

@pytest.fixture
def erp_translations(erp_service):
    class Translations:
        def __init__(self, service):
            self.service = service

        def list(self, field):
            if field == 'def_body_text':
                return {
                    'ca_ES': '',
                    'es_ES': '',
                }
            template = self.service.data.templates[existing_template.xml_id]
            prefix = field+'_'
            return {
                key[len(prefix):] : value
                for key, value in template.items()
                if key.startswith(prefix)
                and value
            }

        def remove(self, field, language):
            translated_field = f'{field}_{language}'
            template = self.service.data.templates[existing_template.xml_id]
            if translated_field in template:
                template[translated_field]=''

        def edit(self, field, lang, values):
            translated_field = f'{field}_{lang}'
            template = self.service.data.templates[existing_template.xml_id]
            if 'value' in values:
                template[translated_field]=values['value']
            if 'lang' in values and values['lang'] != lang:
                template[translated_field] = ''

    return Translations(erp_service)

@pytest.fixture
def erp_backdoor(erp_service):
    """
    Just a way of accessing directly the ERP that can be
    substituted for the ErpServiceDouble.
    """
    class BackendBackdoor:
        def __init__(self, service):
            self.service = service

        def template_fixture_constant_data(self):
            data = self.service.data.templates[existing_template.erp_id]
            return dict(
                id = data['id'],
                name = data['name'],
                model_int_name = data['model_int_name'],
            )

        def resolve_template_fixture_semantic_id(self):
            if existing_template.xml_id not in self.service.data.templates:
                return null
            return self.service.data.templates[existing_template.xml_id]['id']

    return BackendBackdoor(erp_service)

class Test_ErpServiceDouble(ErpService_TestSuite):

    def test__save_template__clonesBodyToItsTranslations(self, erp_translations, erp_backdoor):
        """Body traslations are still a implementation detaiil"""

