INDEX_PM_T = 0
class PoweremailTemplatesTest:
    _fields = ['id', 'def_subject', 'def_subject_es_ES', 'def_subject_ca_ES', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'name', 'model_int_name', 'lang']
    _index = 0

    def __init__(self, ERP, xml_id):
        for field in self._fields:
            if field == 'id':
                setattr(self, field, PoweremailTemplatesTest._index)
            else:
                setattr(self, field, "{}_{}".format(field, xml_id))
        PoweremailTemplatesTest._index += 1

    def read(self, fields):
        PoweremailTemplatesTest._index += 1
        auto_fields = {
            field: "{}_{}".format(field, PoweremailTemplatesTest._index) #PoweremailTemplatesTest._index if field == 'id' else "{}_{}".format(field, PoweremailTemplatesTest._index)
            for field in fields
        }
        auto_fields['model_int_name'] = 'poweremail.templates'
        auto_fields['id'] = PoweremailTemplatesTest._index
        return auto_fields


class ERPTest:
    _models = {'poweremail.templates': PoweremailTemplatesTest}
    _erp_client = 'test_ERP_CLASS'

    @classmethod
    def get_erp_conn(cls):
        return True

    def _connect_with_erp(self):
        try:
            self._erp_client = 'client'
            print("connecting to ERPTEST")
        except:
            pass

    def __getitem__(self, model_name):
        model = self._models.get(model_name)
        if model is None:
            model = PoweremailTemplatesTest
            self._models[model_name] = model

        return model

    def get_object_reference(self, module, name):
        return module, 1

    def test_connection(self):
        return True

    def get_model_id(self, xml_id):
        module, name = xml_id.split('.')
        model, _id = self.get_object_reference(module, name)
        return model, _id

    def get_erp_id(self, xml_id, expected_model='poweremail.templates'):
        model, _id = self.get_model_id(xml_id)

        return _id

    def get_erp_template(self, xml_id=None, id=None):
        if not xml_id and not id:
            raise KeyError("Missing id and xml_id")
        erp_id = None
        if xml_id:
            erp_id = self.get_erp_id(xml_id=xml_id)
        else:
            erp_id = id
        pem_template = PoweremailTemplatesTest(self, erp_id)
        return pem_template
