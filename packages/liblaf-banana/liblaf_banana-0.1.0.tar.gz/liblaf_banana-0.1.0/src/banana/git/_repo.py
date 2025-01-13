import git


def get_repo(*, search_parent_directories: bool = True) -> git.Repo:
    return git.Repo(search_parent_directories=search_parent_directories)
