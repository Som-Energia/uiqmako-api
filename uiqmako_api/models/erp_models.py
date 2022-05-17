import json


class PoweremailTemplates:
    _PoweremailTemplates = None
    _editable_fields = ['def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'lang']
    _fields = _editable_fields + ['id', 'name', 'model_int_name']
    _erp = None

    def __init__(self, ERP, xml_id, erp_id=None):

        self._PoweremailTemplates = ERP['poweremail.templates']
        self._erp = ERP
        if xml_id:
            erp_id = ERP.get_erp_id(xml_id=xml_id, expected_model='poweremail.templates')
        elif not erp_id:
            raise Exception("Can't create Template without info")
        for field, value in self._PoweremailTemplates.read(erp_id, self._fields).items():
            setattr(self, field, value)

    def upload_edit(self, body_text, headers):
        template_fields = json.loads(headers)
        template_fields['def_body_text'] = body_text
        fields_to_write = {
            key: template_fields[key]
            for key in self._editable_fields
        }
        self._PoweremailTemplates.write(self.id, fields_to_write)
        return IrTranslation(self._erp).upload_translation_all(fieldname='def_body_text', model='poweremail.templates', res_id=self.id, value=body_text)



class IrTranslation:
    _IrTranslation = None
    _fields = ['id', 'name', 'lang', 'value', 'res_id', 'src']
    _erp = None

    def __init__(self, ERP):
        self._IrTranslation = ERP['ir.translation']
        self._erp

    def upload_translation_all(self, fieldname, model, res_id, value):
        tr_ids = self._IrTranslation.search([('res_id', '=', res_id), ('name', '=', '{},{}'.format(model,fieldname))])
        return self._IrTranslation.write(tr_ids, {'value': value})
