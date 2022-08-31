from .erp_service_double import ErpServiceDouble

class ERPTest:
    _erp_client = 'test_ERP_CLASS'

    def __init__(self, service=None):
        self._service = service or ErpServiceDouble()

    @classmethod
    def get_erp_conn(cls):
        return True

    def test_connection(self):
        return True

    def service(self):
        return self._service

