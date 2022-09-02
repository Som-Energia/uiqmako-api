import xmlrpc.client

from config import settings
from erppeek import Client, Error, Fault
from pool_transport import PoolTransport

from uiqmako_api.errors.exceptions import UIQMakoBaseException, XmlIdNotFound, InvalidId, CantConnectERP
from uiqmako_api.models.erp_models import PoweremailTemplates
from uiqmako_api.utils.erp_service import ErpService


class ERP:
    _instance = None
    _erp_client = None
    _models = dict()
    _name = None
    _uri = None

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

        try:
            self._erp_client = Client(
                 transport=PoolTransport(secure=False),
                **settings.erp_conn(self._name)
            )
            self._uri = settings.erp_conn(self._name)['server']
        except:
            pass
            #raise CantConnectERP("Unable to connect to {} ERP".format(self._name))

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

    def test_connection(self):
        try:
            self.get_erp_conn().ResUsers.read(1, ['name'])
        except Exception:
            return False
        return True

    def get_object_reference(self, module, name):
        try:
            model, _id = self.get_erp_conn().IrModelData.get_object_reference(module, name)
        except Fault as e:
            raise XmlIdNotFound(msg=e.faultCode)
        return model, _id

    def get_model_id(self, xml_id):
        module, name = xml_id.split('.')
        model, _id = self.get_object_reference(module, name)
        return model, _id

    async def get_object(self, model, id):
        obj = self[model].browse(id)
        return obj

    async def upload_edit(self, body_text, headers, template_xml_id):
        return await PoweremailTemplates.upload_edit(self, xml_id=template_xml_id, body_text=body_text, headers=headers)

    def service(self):
        return ErpService(self._erp_client)

class ERP_PROD(ERP):
    _name = 'PROD'

    def __new__(cls):
        return super().__new__(cls)


class ERP_TESTING(ERP):
    _name = 'TESTING'

    def __new__(cls):
        return super().__new__(cls)


class ERP_LOCAL(ERP):
    _name = 'LOCAL'

    def __new__(cls):
        return super().__new__(cls)
