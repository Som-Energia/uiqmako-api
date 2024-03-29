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
        erp_id = await self.erp_id('poweremail.templates', id)
        try:
            template = dict(self.data.templates[erp_id])
        except KeyError:
            raise XmlIdNotFound(f"No template found with id {id}")

        supported_languages = 'ca_ES', 'es_ES'
        for lang in supported_languages:
            template.setdefault('def_subject_'+lang, '')

        return Template(**template)

    async def save_template(self, id, **kwds):
        erp_id = await self.erp_id('poweremail.templates', id)
        try:
            template = self.data.templates[erp_id]
        except KeyError:
            raise XmlIdNotFound(str(id))
        if 'name' in kwds: del kwds['name']
        if 'id' in kwds: del kwds['id']
        if 'model_int_name' in kwds: del kwds['model_int_name']

        supported_languages = 'ca_ES', 'es_ES'
        for lang in supported_languages:
            subject_lang = 'def_subject_'+lang
            kwds.setdefault(subject_lang, '')

        existing_body_langs = [
            attribute[len('def_body_text_'):]
            for attribute in template.keys()
            if attribute.startswith('def_body_text_')
        ]
        for lang in {*supported_languages, *existing_body_langs}:
            kwds['def_body_text_'+lang] = kwds['def_body_text']

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


