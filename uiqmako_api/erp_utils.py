from config import settings
from erppeek import Client, Error
from pool_transport import PoolTransport


class ERP:
    _instance = None
    _erp_client = None
    _models = dict()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if cls._erp_client is None:
            cls._connect_with_erp(cls)
        return cls._instance

    @classmethod
    def get_erp_conn(cls):
        if cls._erp_client is None:
            cls._connect_with_erp(cls)
        return cls._erp_client

    def _connect_with_erp(self):
        self._erp_client = Client(
            # transport=PoolTransport(secure=False), #TODO: fix error
            **settings.erp_conn()
        )

    def __getitem__(self, model_name):
        model = self._models.get(model_name)
        if model is None:
            try:
                model = self.get_erp_conn().model(model_name)
            except Error as e:
                raise KeyError(str(e))
            else:
                self._models[model_name] = model

        return model

    def get_object_reference(self, module, name):
        return self.get_erp_conn().IrModelData.get_object_reference(module, name)

class PoweremailTemplates:
    _PoweremailTemplates = ERP()['poweremail.templates']
    _fields = ['id', 'def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'name', 'model_int_name', 'lang']

    def __init__(self, template_id):
        for field, value in self._PoweremailTemplates.read(template_id, self._fields).items():
            setattr(self, field, value)


def get_model_id(xml_id):
    module, name = xml_id.split('.')
    model, _id = ERP().get_object_reference(module, name)
    if model != 'poweremail.templates':
        raise ValueError("xml_id does not refer to a Poweremail Template")
    return _id

def get_erp_template(xml_id=None, id=None):
    if not xml_id and not id:
        raise KeyError("Missing id and xml_id")
    erp_id = None
    if xml_id:
        erp_id = get_model_id(xml_id)
    else:
        erp_id = id
    pem_template = PoweremailTemplates(erp_id)
    return pem_template