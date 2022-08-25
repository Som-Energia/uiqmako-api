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
    _supportedLanguages = ['es_ES', 'ca_ES']

    def __init__(self, ERP):
        self._IrTranslation = ERP['ir.translation']
        self._erp

    def upload_translation_all(self, fieldname, model, res_id, value):
        tr_ids = self._IrTranslation.search([('res_id', '=', res_id), ('name', '=', '{},{}'.format(model,fieldname))])
        return self._IrTranslation.write(tr_ids, {'value': value})

    def download_template_subject_translations(self, template_id):
        # Criteria:
        # - ignore not supported languages present in the ERP (schema would reject them)
        # - initialize to '' translations missing in erp
        #   Should be initialized to the def_subject?

        domain =[
            ('name','=','poweremail.templates,def_subject'),
            ('res_id','=',template_id),
        ]
        fields = ['lang', 'value']

        result = {
            'def_subject_'+translation['lang']: translation['value']
            for translation in self._IrTranslation.read(domain, fields) or []
            if translation['lang'] in self._supportedLanguages
        }
        for language in self._supportedLanguages:
            result.setdefault('def_subject_'+language, '')
        return result

    def upload_template_subject_translation(self, template_id, template_fields):
        # TODO: cover test cases:
        # - Edited field existing in the ERP are updated
        # - Edited field not in the ERP are created
        # - Unsupported translations in erp are left as is
        # - Unsupported translations in edited fields are ignored
        # - No translations in erp handled ok
        # - (Not implemented yet) Edited empty fields, not existing in ERP, are ignored
        # - (Not implemented yet) Edited empty fields, existing in ERP, are deleted

        translated_field = 'def_subject'
        modelname = 'poweremail.templates'
        qualified_field = modelname + ',' + translated_field
        prefix = translated_field + '_'

        language_to_create = self._supportedLanguages[:] # copy, it will be edited
        edited_languages = [
            field[len(prefix):]
            for field in template_fields
            if field.startswith(prefix)
        ]

        erp_translations = self._IrTranslation.read([
            ('name', '=', qualified_field),
            ('res_id', '=', template_id),
        ],[])

        # Update existing
        for translation in erp_translations:
            if translation['lang'] not in edited_languages:
                continue
            id = translation['id']
            lang = translation['lang']
            value = translation['value']
            self._IrTranslation.write(id, dict(
                src=template_fields[translated_field],
                value=template_fields[prefix+lang],
            ))
            language_to_create.remove(lang)

        # Create new translations
        for language in language_to_create:
            self._IrTranslation.create(dict(
                type='field',
                name=qualified_field,
                res_id=template_id,
                lang=language,
                src=template_fields[translated_field],
                value=template_fields[prefix+language],
            ))

