import json
from uiqmako_api.utils.erp_service import ErpService

class PoweremailTemplates:
    _editable_fields = ['def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'lang']
    _fields = _editable_fields + ['id', 'name', 'model_int_name']
    _erp = None

    def __init__(self, ERP):
        self._erp = ERP

    @classmethod
    async def load(cls, ERP, xml_id, erp_id=None):
        self = cls(ERP)

        service = ERP.service()
        self = await service.load_template(xml_id or erp_id)
        for field, value in self.dict().items():
            setattr(self, field, value)
        return self

    @classmethod
    async def upload_edit(cls, erp, xml_id, body_text, headers):
        return await erp.service().save_template(**dict(
            json.loads(headers),
            id=xml_id,
            def_body_text=body_text,
        ))

class IrTranslation:
    _IrTranslation = None
    _fields = ['id', 'name', 'lang', 'value', 'res_id', 'src']
    _erp = None
    _supported_languages = ['es_ES', 'ca_ES']

    def __init__(self, ERP):
        self._IrTranslation = ERP['ir.translation']
        self._erp

    def upload_translation_all(self, fieldname, model, res_id, value):
        """
        Sets to the same value all existing translations of the field
        of the model for the given object with res_id.
        This is done this way because the body translations didn't work
        due to a bug in our openerp version.
        """
        tr_ids = self._IrTranslation.search([('res_id', '=', res_id), ('name', '=', '{},{}'.format(model,fieldname))])
        return self._IrTranslation.write(tr_ids, {'value': value})

    def download_template_subject_translations(self, template_id):
        return self.download_translations(
            modelname = 'poweremail.templates',
            object_id = template_id,
            translated_field = 'def_subject',
        )

    def download_translations(self, modelname, object_id, translated_field):
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

    def upload_template_subject_translation(self, template_id, template_fields):
        self.upload_translation(
            modelname = 'poweremail.templates',
            object_id = template_id,
            translated_field = 'def_subject',
            fields = template_fields,
        )

    def upload_translation(self, modelname, object_id, translated_field, fields):
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

