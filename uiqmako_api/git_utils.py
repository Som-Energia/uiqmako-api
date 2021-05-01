from git import Repo


def diff_content(repo: Repo):

    differences = {
        'new_files': repo.untracked_files,
        'changed_files': [item.a_path for item in repo.index.diff(None)]
    }
    return differences
