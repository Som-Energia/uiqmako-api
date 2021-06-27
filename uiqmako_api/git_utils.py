from git import Repo
import os
from yamlns import namespace as ns


def diff_content(repo: Repo):

    differences = {
        'new_files': repo.untracked_files,
        'changed_files': [item.a_path for item in repo.index.diff(None)]
    }
    return differences


def setup_template_repository():
    from config import settings
    repo_path = settings.TEMPLATE_REPO_PATH
    if not os.path.exists(repo_path):
        os.mkdir(repo_path)
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        return Repo.init(repo_path)
    else:
        return Repo(repo_path)


async def create_or_update_template(xml_id, template, git_repo):
    body_filename = 'correu-'+xml_id + '.mako'
    headers_filename = body_filename + '.yaml'
    repo_working_dir = git_repo.working_dir
    text_modified = False
    headers_modified = False
    with open(os.path.join(repo_working_dir, body_filename), 'w') as f:
        f.write(template.def_body_text)
    git_repo.index.add(body_filename)
    if git_repo.is_dirty():
        git_repo.index.add(body_filename)
        text_modified = True
        git_repo.index.commit("update body_text for {}".format(template.name))
    headers_keys = 'cc,to,subject,bcc'.split(',')
    with open(os.path.join(repo_working_dir, headers_filename), 'w') as f:
        for key in headers_keys:
            f.write("{}: {}\n".format(key, template["def_{}".format(key)]))

    git_repo.index.add(headers_filename)
    if git_repo.is_dirty():
        git_repo.index.add(body_filename)
        headers_modified = True
        git_repo.index.commit("update headers for {}".format(template.name))
    return text_modified or headers_modified
