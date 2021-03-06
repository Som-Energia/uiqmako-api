import pytest, os
from uiqmako_api.utils.git import *
from .erp_test import PoweremailTemplatesTest, ERPTest
from uiqmako_api.schemas.templates import Template

GIT = setup_template_repository()


class TestGitUtils:
    from config import settings
    repo_path = settings.TEMPLATE_REPO_PATH

    @staticmethod
    def _write_in_file(filepath, text):
        with open(filepath, 'w') as f:
            f.write(text)

    def test_diff_content__new_file(self, test_app):

        file_path = os.path.join(self.repo_path, 'new_file.mako')
        test_text = "This is a test text\nWith two lines"
        with open(file_path, 'w') as f:
            f.write(test_text)
        result = diff_content(test_app.template_repo)
        assert result == {'new_files': ['new_file.mako'], 'changed_files': []}
        os.remove(file_path)

    def test_diff_content__no_changes(self, test_app):
        result = diff_content(test_app.template_repo)
        assert result == {'new_files': [], 'changed_files': []}

    def test_diff_content__change_in_existing(self, test_app):

        file_path = os.path.join(self.repo_path, 'existing_file.mako')
        self._write_in_file(file_path, "Existing file\nPlus a line")
        result = diff_content(test_app.template_repo)
        assert result == {'new_files': [], 'changed_files': ['existing_file.mako']}
        self._write_in_file(file_path, "Existing file")

    @pytest.mark.asyncio
    async def test_create_or_update_template(self):
        file_name_mako = os.path.join(self.repo_path, 'correu-xml_id_test.mako')
        file_name_yaml = os.path.join(self.repo_path, 'correu-xml_id_test.mako.yaml')
        assert not os.path.exists(file_name_mako)
        assert not os.path.exists(file_name_yaml)
        template = Template.from_orm(PoweremailTemplatesTest(ERP=ERPTest(), xml_id='module.id'))
        a = await create_or_update_template('xml_id_test', template, GIT)
        assert a
        assert os.path.exists(file_name_mako)
        assert os.path.exists(file_name_yaml)

