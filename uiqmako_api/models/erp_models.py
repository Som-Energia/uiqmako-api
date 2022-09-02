import json

class PoweremailTemplates:
    _erp = None

    def __init__(self, ERP):
        self._erp = ERP

    @classmethod
    async def load(cls, ERP, xml_id, erp_id=None):
        service = ERP.service()
        self = await service.load_template(xml_id or erp_id)
        for field, value in self.dict().items():
            setattr(self, field, value)
        return self

