import pytest
from yamlns import ns
from config import settings
from erppeek_wst import ClientWST as Client
from pool_transport import PoolTransport
from uiqmako_api.utils.erp_service import ErpService
from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import InvalidId, XmlIdNotFound
import os

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(not os.environ.get('UIQMAKO_TEST_ERP',False),
        reason="Define UIQMAKO_TEST_ERP environt to run ERP dependant tests"
    ),
]

# Kludge to avoid deletion of cursors wile erppeek_wst 3.0.1 is not released
# See: https://github.com/gisce/erppeek_wst/commit/2b9236b86aa16ab6b675c38f1151757260fc9d0d
from erppeek import Service
Service.__del__ = lambda self: None

# Module Fixtures

@pytest.fixture(scope='module')
def erp_client():
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
def erp_services(rollback_erp):
    return ErpService(rollback_erp)


existing_template = ns(
    # An existing template with semantic id
    erp_id = 183, # Extremely fragile
    xml_id = 'giscedata_switching.notification_atr_M1_01',
    name = 'ATR M101: Solicitud de modificación cambio de titular',
    model = 'giscedata.switching',
    subject_ca_ES =
        'Som Energia: Canvi de titular. Verificació de dades. '
        'Contracte ${object.polissa_ref_id.name}',
    subject_es_ES = 
        'Som Energia: Cambio de titular. Verificación de datos. '
        'Contrato ${object.polissa_ref_id.name}',
)
def edited_values(**kwds):
    result = ns(
        name = "New name",
        model_int_name = "New model",
        def_subject = "New subject",
        def_subject_es_ES = "New subject es",
        def_subject_ca_ES = "New subject ca",
        def_to = "New To",
        def_cc = "New CC",
        def_bcc = "New BCC",
        def_body_text = "New body",
        lang = "New lang",
    )
    return ns(result, **kwds)

# Helpers

class TranslationsHelper():
    """
    Helper to manage the backend
    """
    def __init__(self, erp):
        self.erp = erp
        self.model = 'poweremail.templates'

    def list(self, field):
        translations = self.erp.IrTranslation.read([
            ('name', '=', self.model+','+field),
            ('res_id', '=', existing_template.erp_id),
        ],['lang', 'value'])
        return {
            x['lang']: x['value']
            for x in translations or []
        }

    def remove(self, field, lang):
        translation_id = self.erp.IrTranslation.search([
            ('name', '=', self.model+','+field),
            ('res_id', '=', existing_template.erp_id),
            ('lang', '=', lang),
        ])
        if not translation_id: return
        self.erp.IrTranslation.unlink(translation_id)

    def edit(self, field, lang, values):
        translation_id = self.erp.IrTranslation.search([
            ('name', '=', self.model+','+field),
            ('res_id', '=', existing_template.erp_id),
            ('lang', '=', lang),
        ])
        if not translation_id: return
        self.erp.IrTranslation.write(translation_id, values)

@pytest.fixture
def erp_translations(rollback_erp):
    """
    Fixture that provides a helper to manage translations
    directly on the backend.
    """
    return TranslationsHelper(rollback_erp)

async def test__fixture__existing_template(rollback_erp, erp_translations):
    """
    This test ensures fragile data has the required properties.
    If it fails, please update the refered fixtures
    """
    module, shortname = existing_template.xml_id.split('.')
    externalid = rollback_erp.IrModelData.read([
        ('module', '=', module),
        ('name', '=', shortname),
        ('model', '=', 'poweremail.templates'),
    ], ['res_id'])
    assert externalid, (
        f"ERP has no {existing_template.xml_id} defined for a {model}, "
        f"\nupdate existing_template.xml_id."
    )
    assert externalid[0]['res_id']==existing_template.erp_id, (
        f"This ERP has template '{existing_template.xml_id}' "
        f"pointing to {externalid[0]['res_id']} instead of "
        f"{existing_template.erp_id}. "
        f"\nPlease correct existing_template.erp_id."
    )
    template = rollback_erp.PoweremailTemplates.read([existing_template.erp_id], ['name','model_int_name'])[0]
    assert template == dict(
        id = existing_template.erp_id,
        name = existing_template.name,
        model_int_name = existing_template.model,
    ), (
        f"This ERP has different name for the template {existing_template.xml_id}.\n"
        f"Expected:\n"
        f"{existing_template.name}\n"
        f"But was:\n"
        f"{template['name']}\n"
        f"\nPlease correct existing_template.name."
    )

    translations = erp_translations.list('def_subject')

    assert set(translations.keys()) == set(('ca_ES', 'es_ES')), (
        f"The template {existing_template.xml_id} is expected to have 'def_subject' "
        f"translated to all and just the supported languages."
    )
    assert translations == {
        'ca_ES': existing_template.subject_ca_ES,
        'es_ES': existing_template.subject_es_ES,
    }, (
        f"Subject translations changed in the ERP template {existing_template.xml_id} "
        f"\nPlease, update existing_template.subject_*"
    )
    assert erp_translations.list('def_body_text').keys() == {
        'es_ES',
        'ca_ES',
    }, (
        f"The template {existing_template.xml_id} is expected to have 'def_body_text' "
        f"translated to all and just the supported languages."
    )


# ErpService.template_list

async def test__template_list(erp_services):
    items = await erp_services.template_list()
    template = [
        item for item in items
        if item['xml_id'] == existing_template.xml_id
    ]
    assert template, (
        f"Expected template with semantic id {existing_template.xml_id} not found"
    )
    assert template[0]['name'] == existing_template.name

# ErpService.erp_id

async def test__erp_id__byId(erp_services):
    id = await erp_services.erp_id('poweremail.templates', 1)
    assert id == 1

async def test__erp_id__byStringNumeric(erp_services):
    id = await erp_services.erp_id('poweremail.templates', '1')
    assert id == 1

async def test__erp_id__bySemanticId(erp_services):
    id = await erp_services.erp_id(
        'poweremail.templates',
        existing_template.xml_id,
    )
    assert type(id) == int
    assert id == existing_template.erp_id

async def test__erp_id__badId(erp_services):
    with pytest.raises(InvalidId) as ctx:
        id = await erp_services.erp_id(
            'poweremail.templates',
            'badformattedid',
        )

    assert str(ctx.value) == (
        "Semantic id 'badformattedid' "
        "does not have the expected format 'module.name'"
    )

async def test__erp_id__missingId(erp_services):
    with pytest.raises(XmlIdNotFound) as ctx:
        id = await erp_services.erp_id(
            'poweremail.templates',
            'properlyformated.butmissing',
        )

    assert str(ctx.value) == (
        "properlyformated.butmissing"
    )

# ErpService.load_template

async def test__load_template__byId(erp_services):
    template = await erp_services.load_template(existing_template.erp_id)

    assert type(template) == Template
    assert template.name == existing_template.name

async def test__load_template__bySemanticId(erp_services):
    template = await erp_services.load_template(existing_template.xml_id)

    assert type(template) == Template
    assert template.name == existing_template.name

async def test__load_template__missingId(erp_services):
    with pytest.raises(Exception) as ctx:
        await erp_services.load_template(9999999) # guessing it wont exist

    assert str(ctx.value) == "No template found with id 9999999"

async def test__load_template__includesSubjectTranslations(erp_services):
    template = await erp_services.load_template(existing_template.xml_id)

    assert template.dict(include={
        'def_subject_ca_ES',
        'def_subject_es_ES',
    }) == dict(
        def_subject_es_ES=existing_template.subject_es_ES,
        def_subject_ca_ES=existing_template.subject_ca_ES,
    )

async def test__load_template__missingTranslationAsEmpty(erp_services, erp_translations):
    # When we remove the spanish translation
    erp_translations.remove('def_subject', 'es_ES')

    template = await erp_services.load_template(existing_template.xml_id)

    assert template.dict(include={
        'def_subject_ca_ES',
        'def_subject_es_ES',
    }) == dict(
        def_subject_es_ES='', # this changes
        def_subject_ca_ES=existing_template.subject_ca_ES,
    )

async def test__load_template__unsupportedLanguages_ignored(erp_services, erp_translations):
    # We change the language of the translation
    erp_translations.edit('def_subject', 'es_ES', values=dict(
        lang = 'pt_PT',
    ))

    assert erp_translations.list('def_subject') == dict(
        pt_PT = existing_template.subject_es_ES, # Whe changed the language here
        ca_ES = existing_template.subject_ca_ES,
    )

    template = await erp_services.load_template(existing_template.xml_id)

    # Then the edited translation is ignored
    # There is no es_ES, so empty
    assert 'def_subject_es_ES' in template.dict()
    assert template.def_subject_es_ES == ''
    # pt_PT not supported, so, not included
    assert 'def_subject_pt_PT' not in template.dict()

# ErpService.save_template

async def test__save_template__changingEditableFields(erp_services):
    edited = edited_values()
    await erp_services.save_template(
        id = existing_template.erp_id,
        **edited,
    )

    retrieved = await erp_services.load_template(existing_template.xml_id)

    assert retrieved.dict() == dict(
        edited,
        id = existing_template.erp_id,
        name = existing_template.name, # Unchanged!
        model_int_name = existing_template.model, # Unchanged!
    )

async def test__save_template__emptySubjectTranslation_removesIt(erp_services, erp_translations):
    edited = edited_values(
        def_subject_ca_ES = "", # <- This changes
    )
    await erp_services.save_template(
        id = existing_template.erp_id,
        **edited,
    )

    erp_translations.list('def_subject') == {
        'es_ES': edited.def_subject_es_ES,
        # And the ca_ES is missing
    }

async def test__save_template__missingSubjectTranslations_recreated(erp_services, erp_translations):
    # Given that the template is missing a subject translation
    erp_translations.remove('def_subject', 'es_ES')

    edited = edited_values()
    await erp_services.save_template(
        id = existing_template.erp_id,
        **edited,
    )

    assert erp_translations.list('def_subject') == {
        'es_ES': edited.def_subject_es_ES,
        'ca_ES': edited.def_subject_ca_ES,
    }

async def test__save_template__clonesBodyToItsTranslations(erp_services, erp_translations):
    edited = edited_values()
    await erp_services.save_template(
        id = existing_template.erp_id,
        **edited,
    )

    assert erp_translations.list('def_body_text') == {
        'es_ES': edited.def_body_text,
        'ca_ES': edited.def_body_text,
    }


