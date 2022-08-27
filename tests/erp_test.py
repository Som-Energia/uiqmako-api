from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import XmlIdNotFound, InvalidId
from yamlns import ns

class ERPTest:
    _erp_client = 'test_ERP_CLASS'

    @classmethod
    def get_erp_conn(cls):
        return True

    def service(self):
        return ErpServiceDouble()

    def test_connection(self):
        return True


# TODO: Duplicated in test_erp_services
existing_template = ns(
    # An existing template with semantic id
    erp_id = 183, # Extremely fragile
    xml_id = 'giscedata_switching.notification_atr_M1_01',
    name = 'ATR M101: Solicitud de modificación cambio de titular',
    model = 'giscedata.switching',
    subject_ca_ES =
        'Som Energia: Canvi de titular. Verificació de dades. '
        'Contracte ${object.polissa_ref_id.name}',
    subject_es_ES = 
        'Som Energia: Cambio de titular. Verificación de datos. '
        'Contrato ${object.polissa_ref_id.name}',
)

class ErpServiceDouble():
    """
    Emulates an actual ErpService.
    """
    def __init__(self, data=None):
        self.data = data or ns(
            templates={},
        )
        self.dummyTemplate('som_test.id_test', 100) # test_templates.py
        self.dummyTemplate('module_test.xml_id', 102) # test_api.py
        self.dummyTemplate('template_module.template_01', 103) # db data
        self.dummyTemplate('template_module.template_02', 104) # db data
        self.dummyTemplate('module.id', 105) # test_git_utils.py, test_schemas.py

    def dummyTemplate(self, xml_id, id, **overrides):
        dummy = dict(
            {
                field: f'{field}_{xml_id}'
                for field in [
                    'def_subject',
                    'def_subject_es_ES',
                    'def_subject_ca_ES',
                    'name',
                    'def_body_text',
                    'def_to',
                    'def_cc',
                    'def_bcc',
                    'lang',
                ]
            },
            id = id,
            model_int_name = 'res.partner',
        )
        dummy.update(overrides)
        self.data.templates[xml_id] = dummy
        self.data.templates[int(dummy['id'])] = dummy # intended shared object
        self.data.templates[str(dummy['id'])] = dummy # intended shared object

    async def erp_id(self, model, id):
        if str(id).isdecimal(): return int(id)
        try:
            module, shortname = id.split('.')
        except ValueError:
            raise InvalidId(
                f"Semantic id '{id}' does not have the expected format 'module.name'"
            )
        try:
            return self.data.templates[id]['id']
        except KeyError:
            raise XmlIdNotFound(id)
            raise XmlIdNotFound(f"No template found with id {id}")


    async def load_template(self, id):
        self.erp_id('poweremail.templates', id)
        try:
            return Template(**self.data.templates[id])
        except KeyError:
            raise XmlIdNotFound(f"No template found with id {id}")

    async def save_template(self, id, **kwds):
        self.erp_id('poweremail.templates', id)
        try:
            template = self.data.templates[id]
        except KeyError:
            raise XmlIdNotFound(str(id))
        if 'name' in kwds: del kwds['name']
        if 'id' in kwds: del kwds['id']
        if 'model_int_name' in kwds: del kwds['model_int_name']
        template.update(kwds)

    async def template_list(self):
        return [
            dict(
                xml_id = key,
                erp_id=value['id'],
                name = value['name']
            )
            for key, value in self.data.templates.items()
            if not str(key).isdecimal()
        ]


