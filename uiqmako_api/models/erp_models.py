import json

class PoweremailTemplates:
    _PoweremailTemplates = None
    _editable_fields = ['def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'lang']
    _fields = _editable_fields + ['id', 'name', 'model_int_name']
    _erp = None

    def __init__(self, ERP, xml_id, erp_id=None):

        self._PoweremailTemplates = ERP['poweremail.templates']
        self._erp = ERP
        if not xml_id and not erp_id:
            raise Exception("Either a numeric or a semantic id is required")
        if xml_id:
            erp_id = ERP.get_erp_id(xml_id=xml_id, expected_model='poweremail.templates')
            if not erp_id:
                raise Exception(f"No template found for such a semantic id '{xml_id}'")
        template = self._PoweremailTemplates.read(erp_id, self._fields)
        if not template:
            raise Exception(f"No template with id {erp_id} found")

        for field, value in template.items():
            setattr(self, field, value)

        subject_translations = IrTranslation(self._erp).download_template_subject_translations(erp_id)
        for field, subject in subject_translations.items():
            setattr(self, field, subject)

    # TODO: no regression test!
    def upload_edit(self, body_text, headers):
        template_fields = json.loads(headers)
        template_fields['def_body_text'] = body_text
        fields_to_write = {
            key: template_fields[key]
            for key in self._editable_fields
        }
        self._PoweremailTemplates.write(self.id, fields_to_write)
        translation = IrTranslation(self._erp)
        translation.upload_template_subject_translation(
            template_id=self.id,
            template_fields=template_fields,
        )
        return translation.upload_translation_all(fieldname='def_body_text', model='poweremail.templates', res_id=self.id, value=body_text)

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

