import pytest, os
from uiqmako_api.git_utils import diff_content
class TestGitUtils:
    from config import settings
    repo_path = settings.TEMPLATE_REPO_PATH

    @staticmethod
    def _write_in_file(filepath, text):
        with open(filepath, 'w') as f:
            f.write(text)

    def test_diff_content__new_file(self, test_template_repo):

        file_path = os.path.join(self.repo_path, 'new_file.mako')
        test_text = "This is a test text\nWith two lines"
        with open(file_path, 'w') as f:
            f.write(test_text)
        result = diff_content(test_template_repo)
        assert result == {'new_files': ['new_file.mako'], 'changed_files': []}
        os.remove(file_path)

    def test_diff_content__no_changes(self, test_template_repo):
        result = diff_content(test_template_repo)
        assert result == {'new_files': [], 'changed_files': []}

    def test_diff_content__change_in_existing(self, test_template_repo):

        file_path = os.path.join(self.repo_path, 'existing_file.mako')
        self._write_in_file(file_path, "Existing file\nPlus a line")
        result = diff_content(test_template_repo)
        assert result == {'new_files': [], 'changed_files': ['existing_file.mako']}
        self._write_in_file(file_path, "Existing file")