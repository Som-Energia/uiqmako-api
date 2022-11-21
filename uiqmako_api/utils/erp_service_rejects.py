import xmlrpc.client
import json

from config import settings
from erppeek import Client, Error, Fault
from pool_transport import PoolTransport

from uiqmako_api.schemas.templates import TemplateRejects
from uiqmako_api.errors.exceptions import UIQMakoBaseException, XmlIdNotFound, InvalidId, CantConnectERP
from uiqmako_api.utils.erp_service import ErpService

# TODO: Relocate and derive
class NoSuchExternalId(Exception):
    def __init__(self, erp_instance_name, model, id):
        super().__init__(
            f"ERP instance {erp_instance_name} has no {model} object with external id '{id}'")

TEMPLATE_MODEL = 'giscedata.switching.notify'

class ErpServiceRejects(ErpService):
    """
    Facade that encapsulates all ERP operations in a
    ERP independent interface so that it can be easily
    mocked.
    """
    # Template fields that can be changed
    _template_editable_fields = [
        'notify_text',
        'def_bofy_text',
    ]
    # All template fields
    _template_fields = _template_editable_fields + [
        'id',
        'info_rebuig',
    ]
    # Languages that will be updated (the rest will be ignored)
    _supported_languages = [
        'es_ES',
        'ca_ES',
    ]

    def __init__(self, erpclient):
        super().__init__(erpclient)
        self._SwitchingNotifyTemplate = self.erp.model(TEMPLATE_MODEL)

    async def template_list(self):
        return await self.semantic_ids_for_model(TEMPLATE_MODEL)

    async def semantic_ids_for_model(self, model):
        external_ids = self.erp.model('ir.model.data').read([
            ('model', '=', model),
        ], [
            'module', 'name', 'res_id',
        ])

        if not external_ids:
            return []
        external_ids = {
            x['res_id']: dict(
                erp_id = x['id'],
                xml_id = x['module']+'.'+x['name'],
                name = x['module']+'.'+x['name'],
            )
            for x in external_ids
        }

        names = self.erp.model(model).read(
            [id for id in external_ids.keys()], ['info_rebuig']
        )
        for name in names:
            external_ids[name['id']]['name'] = name['info_rebuig']
        return [x for x in external_ids.values()]


    def erp_id(self, model, id):
        """
        Returns the equivalent numeric erp id for the model.

        - If the id is already numeric or a digit string
          return it as integer.
        - Else it considers it a semantic/external id,
          and it will look up in the current ERP instance
          for an object in the model having such a semantic id.
        """
        if type(id) == int:
            return id

        if id.isdecimal():
            return int(id)

        try:
            module, shortname = id.split('.')
        except ValueError:
            raise InvalidId(
                f"Semantic id '{id}' does not have the expected format 'module.name'"
            )
        externalid = self.erp.IrModelData.read([
            ('module', '=', module),
            ('name', '=', shortname),
            ('model', '=', TEMPLATE_MODEL),
        ], ['res_id'])

        if not externalid:
            raise XmlIdNotFound(id)

        return externalid[0]['res_id']

    async def load_template(self, id):
        erp_id = self.erp_id(TEMPLATE_MODEL, id)
        template = self._SwitchingNotifyTemplate.read([erp_id], self._template_fields)
        if not template:
            raise Exception(f"No template found with id {erp_id}")
        template = template[0]
        template['name'] = template['info_rebuig']
        template['model_int_name'] = 'giscedata.switching'
        template['def_body_text'] = template['notify_text']

        return TemplateRejects(**template)

    # TODO: Should receive a full object or dict not edition fields body and header
    async def save_template(self, id, **fields):
        erp_id = self.erp_id(TEMPLATE_MODEL, id)

        self._SwitchingNotifyTemplate.write(erp_id, {
            key: fields[key]
            for key in self._template_editable_fields
        })

        wiz_obj = self.erp.WizardCleanCache
        wiz_id = wiz_obj.create({})
        wiz_obj.action_clean_cache([wiz_id.id])

