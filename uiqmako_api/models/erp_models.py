import json
from uiqmako_api.utils.erp_service import ErpService

class PoweremailTemplates:
    _editable_fields = ['def_subject', 'def_body_text', 'def_to', 'def_cc', 'def_bcc', 'lang']
    _fields = _editable_fields + ['id', 'name', 'model_int_name']
    _erp = None

    def __init__(self, ERP):
        self._erp = ERP

    @classmethod
    async def load(cls, ERP, xml_id, erp_id=None):
        self = cls(ERP)

        service = ERP.service()
        self = await service.load_template(xml_id or erp_id)
        for field, value in self.dict().items():
            setattr(self, field, value)
        return self

    @classmethod
    async def upload_edit(cls, erp, xml_id, body_text, headers):
        return await erp.service().save_template(**dict(
            json.loads(headers),
            id=xml_id,
            def_body_text=body_text,
        ))


