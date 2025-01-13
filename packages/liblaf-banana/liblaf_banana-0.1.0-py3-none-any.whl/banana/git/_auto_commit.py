import git

import banana as ba


def auto_commit(message: str = "chore(exp): auto commit") -> None:
    if not ba.env.get_bool("BANANA_AUTO_COMMIT", default=True):
        return
    repo: git.Repo = git.Repo(search_parent_directories=True)
    if not repo.is_dirty(untracked_files=True):
        return
    repo.git.add(all=True)
    repo.git.commit(message=message.strip())
