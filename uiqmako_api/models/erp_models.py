

class PoweremailTemplates:
    _PoweremailTemplates = None
    _fields = ['id', 'def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'name', 'model_int_name', 'lang']

    def __init__(self, ERP, xml_id, erp_id=None):

        self._PoweremailTemplates = ERP['poweremail.templates']
        if xml_id:
            erp_id = ERP.get_erp_id(xml_id=xml_id, expected_model='poweremail.templates')
        elif not erp_id:
            raise Exception("Can't create Template without info")
        for field, value in self._PoweremailTemplates.read(erp_id, self._fields).items():
            setattr(self, field, value)


