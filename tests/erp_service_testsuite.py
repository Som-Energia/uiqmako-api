import pytest
from yamlns import ns
from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import InvalidId, XmlIdNotFound

"""
Those are the test that are run for both ErpService and ErpServiceDouble.
They are important to preserve the functionality parity between them
so that tests on the rest of the software can be safely run against
the double.

This test suite refers fixtures that should be implemented in derived classes:

- erp_service: Returns an instance of the ErpService
- erp_backdoor: Encapsulation on some operation performed agains the ERP
- erp_translations: Like erp_backdoor but specialized in erp field translations
"""

pytestmark = [
    pytest.mark.asyncio,
]


# Module Fixtures

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


class ErpService_TestSuite:
    # Fixture testing

    async def test__fixture__existing_template(self, erp_backdoor, erp_translations):
        """
        This test ensures fragile data has the required properties.
        If it fails, please update the referred fixtures
        """
        erp_id = erp_backdoor.resolve_template_fixture_semantic_id()
        assert erp_id, (
            f"ERP has no {existing_template.xml_id} defined for a {model}, "
            f"\nupdate existing_template.xml_id."
        )
        assert erp_id==existing_template.erp_id, (
            f"This ERP has template '{existing_template.xml_id}' "
            f"pointing to {erp_id} instead of "
            f"{existing_template.erp_id}. "
            f"\nPlease correct existing_template.erp_id."
        )
        template = erp_backdoor.template_fixture_constant_data()
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

    async def test__template_list(self, erp_service):
        items = await erp_service.template_list()
        template = [
            item for item in items
            if item['xml_id'] == existing_template.xml_id
        ]
        assert template, (
            f"Expected template with semantic id {existing_template.xml_id} not found"
        )
        assert template[0]['name'] == existing_template.name

    # ErpService.erp_id

    async def test__erp_id__byId(self, erp_service):
        id = await erp_service.erp_id('poweremail.templates', 1)
        assert id == 1

    async def test__erp_id__byStringNumeric(self, erp_service):
        id = await erp_service.erp_id('poweremail.templates', '1')
        assert id == 1

    async def test__erp_id__bySemanticId(self, erp_service):
        id = await erp_service.erp_id(
            'poweremail.templates',
            existing_template.xml_id,
        )
        assert type(id) == int
        assert id == existing_template.erp_id

    async def test__erp_id__badId(self, erp_service):
        with pytest.raises(InvalidId) as ctx:
            id = await erp_service.erp_id(
                'poweremail.templates',
                'badformattedid',
            )

        assert str(ctx.value) == (
            "Semantic id 'badformattedid' "
            "does not have the expected format 'module.name'"
        )

    async def test__erp_id__missingId(self, erp_service):
        with pytest.raises(XmlIdNotFound) as ctx:
            id = await erp_service.erp_id(
                'poweremail.templates',
                'properlyformated.butmissing',
            )

        assert str(ctx.value) == (
            "properlyformated.butmissing"
        )

    # ErpService.load_template

    async def test__load_template__byId(self, erp_service):
        template = await erp_service.load_template(existing_template.erp_id)

        assert type(template) == Template
        assert template.name == existing_template.name

    async def test__load_template__bySemanticId(self, erp_service):
        template = await erp_service.load_template(existing_template.xml_id)

        assert type(template) == Template
        assert template.name == existing_template.name

    async def test__load_template__missingId(self, erp_service):
        with pytest.raises(Exception) as ctx:
            await erp_service.load_template(9999999) # guessing it wont exist

        assert str(ctx.value) == "No template found with id 9999999"

    async def test__load_template__includesSubjectTranslations(self, erp_service):
        template = await erp_service.load_template(existing_template.xml_id)

        assert template.dict(include={
            'def_subject_ca_ES',
            'def_subject_es_ES',
        }) == dict(
            def_subject_ca_ES=existing_template.subject_ca_ES,
            def_subject_es_ES=existing_template.subject_es_ES,
        )

    async def test__load_template__missingTranslationAsEmpty(self, erp_service, erp_translations):
        # When we remove the spanish translation
        erp_translations.remove('def_subject', 'es_ES')

        template = await erp_service.load_template(existing_template.xml_id)

        assert template.dict(include={
            'def_subject_ca_ES',
            'def_subject_es_ES',
        }) == dict(
            def_subject_ca_ES=existing_template.subject_ca_ES,
            def_subject_es_ES='', # this changes
        )

    async def test__load_template__noTranslation(self, erp_service, erp_translations):
        # When we remove all the translations
        erp_translations.remove('def_subject', 'es_ES')
        erp_translations.remove('def_subject', 'ca_ES')

        template = await erp_service.load_template(existing_template.xml_id)

        assert template.dict(include={
            'def_subject_ca_ES',
            'def_subject_es_ES',
        }) == dict(
            def_subject_ca_ES='', # this changes
            def_subject_es_ES='', # this changes
        )

    async def test__load_template__unsupportedLanguages_ignored(self, erp_service, erp_translations):
        # We change the language of the translation
        erp_translations.edit('def_subject', 'es_ES', values=dict(
            lang = 'pt_PT',
        ))
        # No Double compatible
        """
        assert erp_translations.list('def_subject') == dict(
            pt_PT = existing_template.subject_es_ES, # Whe changed the language here
            ca_ES = existing_template.subject_ca_ES,
        )
        """
        template = await erp_service.load_template(existing_template.xml_id)

        # Then the edited translation is ignored
        # There is no es_ES, so empty
        assert 'def_subject_es_ES' in template.dict()
        assert template.def_subject_es_ES == ''
        # pt_PT not supported, so, not included
        assert 'def_subject_pt_PT' not in template.dict()

    # ErpService.save_template

    async def test__save_template__changingEditableFields(self, erp_service):
        edited = edited_values()
        await erp_service.save_template(
            id = existing_template.erp_id,
            **edited,
        )

        retrieved = await erp_service.load_template(existing_template.xml_id)

        assert retrieved.dict() == dict(
            edited,
            id = existing_template.erp_id,
            name = existing_template.name, # Unchanged!
            model_int_name = existing_template.model, # Unchanged!
        )

    async def test__save_template__usingSemanticId(self, erp_service):
        edited = edited_values()
        await erp_service.save_template(
            id = existing_template.xml_id,
            **edited,
        )

        retrieved = await erp_service.load_template(existing_template.xml_id)

        assert retrieved.dict() == dict(
            edited,
            id = existing_template.erp_id,
            name = existing_template.name, # Unchanged!
            model_int_name = existing_template.model, # Unchanged!
        )

    async def test__save_template__emptySubjectTranslation_removesIt(self, erp_service, erp_translations):
        edited = edited_values(
            def_subject_ca_ES = "", # <- This changes
        )
        await erp_service.save_template(
            id = existing_template.erp_id,
            **edited,
        )

        erp_translations.list('def_subject') == {
            'es_ES': edited.def_subject_es_ES,
            # And the ca_ES is missing
        }

    async def test__save_template__missingSubjectTranslations_recreated(self, erp_service, erp_translations):
        # Given that the template is missing a subject translation
        erp_translations.remove('def_subject', 'es_ES')

        edited = edited_values()
        await erp_service.save_template(
            id = existing_template.erp_id,
            **edited,
        )

        assert erp_translations.list('def_subject') == {
            'es_ES': edited.def_subject_es_ES,
            'ca_ES': edited.def_subject_ca_ES,
        }

    async def test__save_template__clonesBodyToItsTranslations(self, erp_service, erp_translations):
        edited = edited_values()
        await erp_service.save_template(
            id = existing_template.erp_id,
            **edited,
        )

        assert erp_translations.list('def_body_text') == {
            'es_ES': edited.def_body_text,
            'ca_ES': edited.def_body_text,
        }


