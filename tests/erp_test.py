from uiqmako_api.schemas.templates import Template
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
        self.dummyTemplate(
            xml_id = existing_template.xml_id,
            id = existing_template.erp_id,
            def_subject = "Untranslated subject",
            def_subject_es_ES = existing_template.subject_es_ES,
            def_subject_ca_ES = existing_template.subject_ca_ES,
            name = existing_template.name,
            model_int_name = existing_template.model,
        ) # TODO: b2b case with the real one

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

    async def load_template(self, id):
        try:
            return Template(**self.data.templates[id])
        except KeyError:
            raise

    async def save_template(self, id, **kwds):
        try:
            template = self.data[id]
        except KeyError:
            raise
        template.update(kwds)

