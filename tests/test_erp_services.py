import pytest
from yamlns import ns
from config import settings
from erppeek_wst import ClientWST as Client
from pool_transport import PoolTransport
from uiqmako_api.utils.erp_service import ErpService
from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import InvalidId, XmlIdNotFound
import os

pytestmark = pytest.mark.skipif(not os.environ.get('UIQMAKO_TEST_ERP',False),
    reason="Define UIQMAKO_TEST_ERP environt to run ERP dependant tests"
)

# Patch to avoid deletion of cursors wile erppeek_wst 3.0.1 is not released
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
def erp(rollback_erp):
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

def erp_translations(rollback_erp, model, field, erp_id):
    translations = rollback_erp.IrTranslation.read([
        ('name', '=', model+','+field),
        ('res_id', '=', erp_id),
    ],['lang', 'value'])
    return {
        x['lang']: x['value']
        for x in translations or []
    }

def remove_erp_translation(rollback_erp, model, field, erp_id, lang):
    translation_id = rollback_erp.IrTranslation.search([
        ('name', '=', model+','+field),
        ('res_id', '=', erp_id),
        ('lang', '=', lang),
    ])
    if not translation_id: return
    rollback_erp.IrTranslation.unlink(translation_id)

def change_erp_translation(rollback_erp, model, field, erp_id, lang, values):
    translation_id = rollback_erp.IrTranslation.search([
        ('name', '=', model+','+field),
        ('res_id', '=', erp_id),
        ('lang', '=', lang),
    ])
    if not translation_id: return
    rollback_erp.IrTranslation.write(translation_id, values)


@pytest.mark.asyncio
async def test__fixture__existing_template(rollback_erp):
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

    translations = erp_translations(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id,
    )
    assert set(translations.keys()) == set(('ca_ES', 'es_ES')), (
        f"The fixture is expecte to have all and just the supported languages"
    )
    assert translations == {
        'ca_ES': existing_template.subject_ca_ES,
        'es_ES': existing_template.subject_es_ES,
    }, (
        f"Subject translations changed in the ERP template {existing_template.xml_id} "
        f"\nPlease, update existing_template.subject_*"
    )


# ErpService.template_list

@pytest.mark.asyncio
async def test__template_list(erp):
    items = await erp.template_list()
    template = [
        item for item in items
        if item['xml_id'] == existing_template.xml_id
    ]
    assert template, (
        f"Expected template with semantic id {existing_template.xml_id} not found"
    )
    assert template[0]['name'] == existing_template.name

# ErpService.erp_id

@pytest.mark.asyncio
async def test__erp_id__byId(erp):
    id = await erp.erp_id('poweremail.templates', 1)
    assert id == 1

@pytest.mark.asyncio
async def test__erp_id__byStringNumeric(erp):
    id = await erp.erp_id('poweremail.templates', '1')
    assert id == 1

@pytest.mark.asyncio
async def test__erp_id__bySemanticId(erp):
    id = await erp.erp_id(
        'poweremail.templates',
        existing_template.xml_id,
    )
    assert type(id) == int
    assert id == existing_template.erp_id

@pytest.mark.asyncio
async def test__erp_id__badId(erp):
    with pytest.raises(InvalidId) as ctx:
        id = await erp.erp_id(
            'poweremail.templates',
            'badformattedid',
        )

    assert str(ctx.value) == (
        "Semantic id 'badformattedid' "
        "does not have the expected format 'module.name'"
    )

@pytest.mark.asyncio
async def test__erp_id__missingId(erp):
    with pytest.raises(XmlIdNotFound) as ctx:
        id = await erp.erp_id(
            'poweremail.templates',
            'properlyformated.butmissing',
        )

    assert str(ctx.value) == (
        "properlyformated.butmissing"
    )

# ErpService.load_template

@pytest.mark.asyncio
async def test__load_template__byId(rollback_erp):
    erp = ErpService(rollback_erp)

    template = await erp.load_template(existing_template.erp_id)

    assert type(template) == Template
    assert template.name == existing_template.name

@pytest.mark.asyncio
async def test__load_template__bySemanticId(rollback_erp):
    erp = ErpService(rollback_erp)

    template = await erp.load_template(existing_template.xml_id)

    assert type(template) == Template
    assert template.name == existing_template.name

@pytest.mark.asyncio
async def test__load_template__missingId(rollback_erp):
    erp = ErpService(rollback_erp)

    with pytest.raises(Exception) as ctx:
        await erp.load_template(9999999) # guessing it wont exist

    assert str(ctx.value) == "No template found with id 9999999"

@pytest.mark.asyncio
async def test__load_template__includesSubjectTranslations(rollback_erp):
    erp = ErpService(rollback_erp)

    template = await erp.load_template(existing_template.xml_id)

    assert template.dict(include={
        'def_subject_ca_ES',
        'def_subject_es_ES',
    }) == dict(
        def_subject_es_ES=existing_template.subject_es_ES,
        def_subject_ca_ES=existing_template.subject_ca_ES,
    )

@pytest.mark.asyncio
async def test__load_template__missingTranslationAsEmpty(rollback_erp):
    erp = ErpService(rollback_erp)

    # When we remove the spanish translation
    translation_id = rollback_erp.IrTranslation.search([
        ('name', '=', 'poweremail.templates,def_subject'),
        ('res_id', '=', existing_template.erp_id),
        ('lang', '=', 'es_ES'),
    ])
    rollback_erp.IrTranslation.unlink(translation_id)

    template = await erp.load_template(existing_template.xml_id)

    assert template.dict(include={
        'def_subject_ca_ES',
        'def_subject_es_ES',
    }) == dict(
        def_subject_es_ES='', # this changes
        def_subject_ca_ES=existing_template.subject_ca_ES,
    )

@pytest.mark.asyncio
async def test__load_template__unsupportedLanguages_ignored(rollback_erp):
    erp = ErpService(rollback_erp)

    # We change the language of the translation
    change_erp_translation(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id,
        'es_ES',
        values = dict(lang = 'pt_PT')
    )

    assert erp_translations(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id,
    ) == dict(
        pt_PT = existing_template.subject_es_ES, # Whe changed the language here
        ca_ES = existing_template.subject_ca_ES,
    )

    template = await erp.load_template(existing_template.xml_id)

    # Then the edited translation is ignored
    # There is no es_ES, so empty
    assert 'def_subject_es_ES' in template.dict()
    assert template.def_subject_es_ES == ''
    # pt_PT not supported, so, not included
    assert 'def_subject_pt_PT' not in template.dict()

# ErpService.save_template

@pytest.mark.asyncio
async def test__save_template__changingEditableFields(rollback_erp):
    erp = ErpService(rollback_erp)
    new_values = edited_values()
    await erp.save_template(
        id = existing_template.erp_id,
        **new_values,
    )

    retrieved = await erp.load_template(existing_template.xml_id)

    assert retrieved.dict() == dict(
        new_values,
        id = existing_template.erp_id,
        name = existing_template.name, # Unchanged!
        model_int_name = existing_template.model, # Unchanged!
    )

@pytest.mark.asyncio
async def test__save_template__emptySubjectTranslation_removesIt(rollback_erp):
    erp = ErpService(rollback_erp)
    new_values = edited_values(
        def_subject_ca_ES = "", # <- This changes
    )
    await erp.save_template(
        id = existing_template.erp_id,
        **new_values,
    )

    translations = erp_translations(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id
    )
    assert translations == {
        'es_ES': new_values.def_subject_es_ES,
        # And the ca_ES is missing
    }

@pytest.mark.asyncio
async def test__save_template__missingSubjectTranslations_recreated(rollback_erp):
    # Given that the template is missing a subject translation
    remove_erp_translation(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id,
        'es_ES',
    )

    erp = ErpService(rollback_erp)

    new_values = edited_values()
    await erp.save_template(
        id = existing_template.erp_id,
        **new_values,
    )

    assert erp_translations(
        rollback_erp,
        'poweremail.templates',
        'def_subject',
        existing_template.erp_id
    ) == {
        'es_ES': new_values.def_subject_es_ES,
        'ca_ES': new_values.def_subject_ca_ES,
    }

@pytest.mark.asyncio
async def test__save_template__clonesBodyToItsTranslations(rollback_erp):
    erp = ErpService(rollback_erp)

    new_values = edited_values()
    await erp.save_template(
        id = existing_template.erp_id,
        **new_values,
    )

    assert erp_translations(
        rollback_erp,
        'poweremail.templates',
        'def_body_text',
        existing_template.erp_id
    ) == {
        'es_ES': new_values.def_body_text,
        'ca_ES': new_values.def_body_text,
    }


