from uiqmako_api.schemas.templates import Template
from uiqmako_api.errors.exceptions import XmlIdNotFound, InvalidId
from yamlns import ns

class ErpServiceDouble():
    """
    Emulates an actual ErpService.
    """
    def __init__(self, data=None):
        self.data = data or ns(
            templates=ns()
        )
        self.add_dummy_template('som_test.id_test', 100) # test_templates.py
        self.add_dummy_template('module_test.xml_id', 102) # test_api.py
        self.add_dummy_template('template_module.template_01', 103) # db data
        self.add_dummy_template('template_module.template_02', 104) # db data
        self.add_dummy_template('module.id', 105) # test_git_utils.py, test_schemas.py

    def add_dummy_template(self, xml_id, id, **overrides):
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


    async def load_template(self, id):
        await self.erp_id('poweremail.templates', id)
        try:
            return Template(**self.data.templates[id])
        except KeyError:
            raise XmlIdNotFound(f"No template found with id {id}")

    async def save_template(self, id, **kwds):
        await self.erp_id('poweremail.templates', id)
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

