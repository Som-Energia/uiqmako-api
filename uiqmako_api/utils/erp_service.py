import xmlrpc.client

from config import settings
from erppeek import Client, Error, Fault
from pool_transport import PoolTransport

from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import UIQMakoBaseException, XmlIdNotFound, InvalidId, CantConnectERP

# TODO: Relocate and derive
class NoSuchExternalId(Exception):
    def __init__(self, erp_instance_name, model, id):
        super().__init__(
            f"ERP instance {erp_instance_name} has no {model} object with external id '{id}'")

class ErpService(object):
    """
    Facade that encapsulates all ERP operations in a
    ERP independent interface so that it can be easily
    mocked.
    """
    # Template fields that can be changed
    _template_editable_fields = [
        'def_subject',
        'def_body_text',
        'def_to',
        'def_cc',
        'def_bcc',
        'lang',
    ]
    # All template fields
    _template_fields = _template_editable_fields + [
        'id',
        'name',
        'model_int_name',
    ]
    # Languages that will be updated (the rest will be ignored)
    _supported_languages = [
        'es_ES',
        'ca_ES',
    ]

    def __init__(self, erpclient):
        self.erp = erpclient
        self._PoweremailTemplates = self.erp.model('poweremail.templates')
        self._IrTranslation = self.erp.model('ir.translation')

    async def template_list(self):
        return await self.semantic_ids_for_model('poweremail.templates')

    async def semantic_ids_for_model(self, model):
        external_ids = self.erp.model('ir.model.data').read([
            ('model', '=', model),
        ], [
            'module', 'name', 'res_id',
        ])

        if not external_ids:
            return []
        external_ids = {
            x['res_id']: dict(
                erp_id = x['id'],
                xml_id = x['module']+'.'+x['name'],
                name = x['module']+'.'+x['name'],
            )
            for x in external_ids
        }

        names = self.erp.model(model).read(
            [id for id in external_ids.keys()], ['name']
        )
        for name in names:
            external_ids[name['id']]['name'] = name['name']
        return [x for x in external_ids.values()]


    async def erp_id(self, model, id):
        """
        Returns the equivalent numeric erp id for the model.

        - If the id is already numeric or a digit string
          return it as integer.
        - Else it considers it a semantic/external id,
          and it will look up in the current ERP instance
          for an object in the model having such a semantic id.
        """
        if type(id) == int:
            return id

        if id.isdecimal():
            return int(id)

        try:
            module, shortname = id.split('.')
        except ValueError:
            raise InvalidId(
                f"Semantic id '{id}' does not have the expected format 'module.name'"
            )
        externalid = self.erp.IrModelData.read([
            ('module', '=', module),
            ('name', '=', shortname),
            ('model', '=', model),
        ], ['res_id'])

        if not externalid:
            raise XmlIdNotFound(id)

        return externalid[0]['res_id']

    async def load_template(self, id):
        erp_id = await self.erp_id('poweremail.templates', id)
        template = self._PoweremailTemplates.read([erp_id], self._template_fields)
        if not template:
            raise Exception(f"No template found with id {erp_id}")
        template = template[0]

        subject_translations = await self.load_translations(
            modelname = 'poweremail.templates',
            object_id = erp_id,
            translated_field = 'def_subject',
        )
        template.update(subject_translations)

        return Template(**template)

    # TODO: Should receive a full object or dict not edition fields body and header
    async def save_template(self, id, **fields):
        erp_id = await self.erp_id('poweremail.templates', id)

        self._PoweremailTemplates.write(erp_id, {
            key: fields[key]
            for key in self._template_editable_fields
        })

        await self.save_translation(
            modelname = 'poweremail.templates',
            object_id = erp_id,
            translated_field = 'def_subject',
            fields = fields,
        )
        # Because laguage selction for body translation is not properly
        # working right now, we are currenly copying the body to all
        # translations and do language selection inside the mako template.
        body_translations = dict(
            {
                'def_body_text_' + lang: fields['def_body_text']
                for lang in self._supported_languages
            },
            def_body_text=fields['def_body_text'],
        )
        await self.save_translation(
            modelname = 'poweremail.templates',
            object_id = erp_id,
            translated_field = 'def_body_text',
            fields = body_translations,
        )
        #translation.upload_translation_all(fieldname='def_body_text', model='poweremail.templates', res_id=self.id, value=body_text)

    async def load_translations(self, modelname, object_id, translated_field):
        # Criteria:
        # - ignore not supported languages present in the ERP (schema would reject them)
        # - initialize to '' translations missing in erp
        #   Should be initialized to the def_subject?
        prefix = translated_field + '_'
        qualified_field = modelname + ',' + translated_field

        domain =[
            ('name', '=', qualified_field),
            ('res_id', '=', object_id),
        ]
        fields = ['lang', 'value']

        result = {
            prefix + translation['lang']: translation['value']
            for translation in self._IrTranslation.read(domain, fields) or []
            if translation['lang'] in self._supported_languages
        }
        for language in self._supported_languages:
            result.setdefault(prefix + language, '')
        return result

    async def save_translation(self, modelname, object_id, translated_field, fields):
        # TODO: test cases checked by hand (for coverage):
        # - Edited field translation existing in the ERP are updated
        # - Edited field translation not in the ERP are created
        # - Unsupported translations in erp are left as is
        # - Unsupported translations in edited fields are ignored
        # - No translations in erp handled ok
        # - Edited empty fields, existing in ERP, are deleted
        # - Edited empty fields, not existing in ERP, are ignored

        qualified_field = modelname + ',' + translated_field
        prefix = translated_field + '_'
        untranslated_value = fields[translated_field]

        language_to_create = self._supported_languages[:] # copy, it will be edited
        edited_languages = [
            field[len(prefix):]
            for field in fields
            if field.startswith(prefix)
        ]

        erp_translations = self._IrTranslation.read([
            ('name', '=', qualified_field),
            ('res_id', '=', object_id),
        ],[])

        # Update existing
        for translation in erp_translations:
            translation_id = translation['id']
            lang = translation['lang']

            if lang not in edited_languages:
                continue

            language_to_create.remove(lang)

            if not fields[prefix + lang]:
                self._IrTranslation.unlink(translation_id)
                continue

            self._IrTranslation.write(translation_id, dict(
                src=untranslated_value,
                value=fields[prefix+lang],
            ))

        # Create new translations
        for lang in language_to_create:
            if not fields[prefix + lang]:
                continue
            self._IrTranslation.create(dict(
                type='field',
                name=qualified_field,
                res_id=object_id,
                lang=lang,
                src=untranslated_value,
                value=fields[prefix + lang],
            ))

