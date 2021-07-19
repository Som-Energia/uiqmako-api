import json


class PoweremailTemplates:
    _PoweremailTemplates = None
    _editable_fields = ['def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'lang']
    _fields = _editable_fields + ['id', 'name', 'model_int_name']
    _erp = None

    def __init__(self, ERP, xml_id, erp_id=None):

        self._PoweremailTemplates = ERP['poweremail.templates']
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
        return self._PoweremailTemplates.write(self.id, fields_to_write)
