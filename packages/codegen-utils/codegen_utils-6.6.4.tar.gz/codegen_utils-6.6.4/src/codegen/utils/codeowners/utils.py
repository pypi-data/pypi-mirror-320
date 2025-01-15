import logging

from codeowners import CodeOwners

logger = logging.getLogger(__name__)


def get_filepath_owners(codeowners: CodeOwners, filepath: str) -> set[str]:
    filename_owners = codeowners.of(filepath)
    return {owner[1] for owner in filename_owners}


def is_path_owned_by_codeowner(codeowners: CodeOwners, path: str, codeowner: str) -> bool:
    filename_owners = codeowners.of(path)
    for owner in filename_owners:
        if owner[1] == codeowner:
            return True
    return False
