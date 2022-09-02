import pytest, os
from uiqmako_api.utils.git import *
from .erp_test import ERPTest
from uiqmako_api.models.erp_models  import PoweremailTemplates
from uiqmako_api.schemas.templates import Template

class TestGitUtils:
    from config import settings
    repo_path = settings.TEMPLATE_REPO_PATH

    @staticmethod
    def _write_in_file(filepath, text):
        with open(filepath, 'w') as f:
            f.write(text)

    def test_diff_content__new_file(self, gitrepo):
        file_path = os.path.join(gitrepo.working_dir, 'new_file.mako')
        test_text = "This is a test text\nWith two lines"
        self._write_in_file(file_path, test_text)
        result = diff_content(gitrepo)
        assert result == {'new_files': ['new_file.mako'], 'changed_files': []}

    def test_diff_content__no_changes(self, gitrepo):
        result = diff_content(gitrepo)
        assert result == {'new_files': [], 'changed_files': []}

    def test_diff_content__change_in_existing(self, gitrepo):
        file_path = os.path.join(gitrepo.working_dir, 'existing_file.mako')
        self._write_in_file(file_path, "Existing file\nPlus a line")
        result = diff_content(gitrepo)
        assert result == {'new_files': [], 'changed_files': ['existing_file.mako']}

    @pytest.mark.asyncio
    async def test_create_or_update_template(self, test_app, gitrepo):
        file_name_mako = os.path.join(gitrepo.working_dir, 'correu-xml_id_test.mako')
        file_name_yaml = os.path.join(gitrepo.working_dir, 'correu-xml_id_test.mako.yaml')
        assert not os.path.exists(file_name_mako)
        assert not os.path.exists(file_name_yaml)
        pem_template = await PoweremailTemplates.load(ERP=ERPTest(), xml_id='module.id')
        template = Template.from_orm(pem_template)
        a = await create_or_update_template('xml_id_test', template, test_app.template_repo)
        assert a
        assert os.path.exists(file_name_mako)
        assert os.path.exists(file_name_yaml)

