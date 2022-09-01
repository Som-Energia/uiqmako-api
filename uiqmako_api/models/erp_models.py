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

    @classmethod
    async def upload_edit(cls, erp, xml_id, body_text, headers):
        return await erp.service().save_template(**dict(
            json.loads(headers),
            id=xml_id,
            def_body_text=body_text,
        ))
