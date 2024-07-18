from typing import Iterable

from dsp_permissions_scripts.models import group

PACKAGE_NAME = "dsp-permissions-scripts"
KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"


def dereference_prefix(
    identifier: str,
    context: dict[str, str],
) -> str:
    """
    Replaces the prefix of an identifier by what the prefix stands for,
    and returns the full IRI of the given identifier.

    Args:
        identifier: an identifier, e.g. "knora-admin:Creator"
        context: The context to use for dereferencing

    Returns:
        The full IRI of the given identifier, e.g. "http://www.knora.org/ontology/knora-admin#Creator"
    """
    namespace_prefix, localname = identifier.split(":")
    return context[namespace_prefix] + localname


def _get_sort_pos_of_custom_group(group: str) -> int:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    relevant_letter = group.replace("knora-admin:", "")[0]
    return alphabet.index(relevant_letter.lower()) + 99  # must be higher than the highest index of the builtin groups


def sort_groups(groups_original: Iterable[group.Group]) -> list[group.Group]:
    """
    Sorts groups:
     - First according to their power (most powerful first - only applicable for built-in groups)
     - Then alphabetically (custom groups)
    """
    sort_key = [
        group.SYSTEM_ADMIN,
        group.CREATOR,
        group.PROJECT_ADMIN,
        group.PROJECT_MEMBER,
        group.KNOWN_USER,
        group.UNKNOWN_USER,
    ]
    groups = list(groups_original)
    groups.sort(key=lambda x: sort_key.index(x) if x in sort_key else _get_sort_pos_of_custom_group(x.val))
    return groups
