import pytest
from .erp_service_testsuite import (
    existing_template,
    ErpService_TestSuite,
)
from config import settings
from erppeek_wst import ClientWST as Client
from pool_transport import PoolTransport
from uiqmako_api.utils.erp_service import ErpService
import os

"""
ERP tests use a rolling-back transaction fixture,
that undoes any ERP changes after the test.
The connection `erp_client` is shared by the module (could be wider).
The transaction `rollback_erp`is per test function/method.

ERP tests are slow and require access to SomEnergia intranet, so,
any test using the erp_client fixture, is skiped by default
unless UIQMAKO_TEST_ERP environ is defined.

All ERP related functionality has been encapsulated inside
the facade ErpService. Its users can be tested without
touching the ERP by using the blackbox equivalent ErpServiceDouble.

In order to preserve blackbox parity both classes pass
the ErpService_TestSuite.

When the suite needs to access the ERP, or the underlying
implementation for the double, such access is encasulated
in fixtures, like erp_translations or erp_backdoor,
that can be redefined by the concrete tests of each Facade.
"""

pytestmark = [
    pytest.mark.asyncio,
]

# Kludge to avoid deletion of cursors wile erppeek_wst 3.0.1 is not released
# See: https://github.com/gisce/erppeek_wst/commit/2b9236b86aa16ab6b675c38f1151757260fc9d0d
from erppeek import Service
Service.__del__ = lambda self: None

# Module Fixtures

@pytest.fixture(scope='module')
def erp_client():
    if not os.environ.get('UIQMAKO_TEST_ERP',False):
        pytest.skip(
            reason="Define UIQMAKO_TEST_ERP environt to run ERP dependant tests"
        )
    client = Client(
        # TODO: take secure from url method
        transport=PoolTransport(secure=False),
        **settings.erp_conn('TESTING')
    )
    yield client

@pytest.fixture()
def rollback_erp(erp_client):
    """
    A connection to erp that will rollback any
    modifications after the test.
    """
    t = erp_client.begin()
    try:
        yield t
    finally:
        t.rollback()
        t.close()

@pytest.fixture()
def erp_service(rollback_erp):
    return ErpService(rollback_erp)

@pytest.fixture
def erp_translations(rollback_erp):
    """
    Fixture that provides a helper to manage translations
    directly on the backend.
    """
    class TranslationsHelper():
        """
        Helper to manage the backend
        """
        def __init__(self, erp):
            self.erp = erp
            self.model = 'poweremail.templates'

        def list(self, field):
            supported_languages = ['ca_ES', 'es_ES']
            translations = self.erp.IrTranslation.read([
                ('name', '=', self.model+','+field),
                ('res_id', '=', existing_template.erp_id),
            ],['lang', 'value'])
            return {
                x['lang']: x['value']
                for x in translations or [] if x['value'] and x['lang'] in supported_languages
            }

        def remove(self, field, lang):
            translation_id = self.erp.IrTranslation.search([
                ('name', '=', self.model+','+field),
                ('res_id', '=', existing_template.erp_id),
                ('lang', '=', lang),
            ])
            if not translation_id: return
            self.erp.IrTranslation.unlink(translation_id)

        def edit(self, field, lang, values, create=False):
            translation_id = self.erp.IrTranslation.search([
                ('name', '=', self.model+','+field),
                ('res_id', '=', existing_template.erp_id),
                ('lang', '=', lang),
            ])
            if translation_id:
                self.erp.IrTranslation.write(translation_id, values)
                return
            if not create: return
            self.erp.IrTranslation.create(dict(
                dict(
                    name= self.model+','+field,
                    res_id=existing_template.erp_id,
                    lang=lang,
                ),
                **values, # values overwrite name, res_id and lang
            ))

    return TranslationsHelper(rollback_erp)

@pytest.fixture
def erp_backdoor(rollback_erp):
    """
    Just a way of accessing directly the ERP so that it can be
    replaced for ErpServiceDouble.
    """
    class BackendBackdoor:
        def __init__(self, erp):
            self.erp = erp

        def template_fixture_constant_data(self):
            return self.erp.PoweremailTemplates.read(
                [existing_template.erp_id],
                ['name','model_int_name']
            )[0]

        def resolve_template_fixture_semantic_id(self):
            module, shortname = existing_template.xml_id.split('.')
            external_id = rollback_erp.IrModelData.read([
                ('module', '=', module),
                ('name', '=', shortname),
                ('model', '=', 'poweremail.templates'),
            ], ['res_id'])
            return external_id[0]['res_id'] if external_id else None

    return BackendBackdoor(rollback_erp)

class Test_ErpService(ErpService_TestSuite):
    pass


