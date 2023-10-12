from dsp_permissions_scripts.models import builtin_groups


def dereference_prefix(
    identifier: str, 
    context: dict[str, str],
) -> str:
    prefix, actual_id = identifier.split(":")
    return context[prefix] + actual_id


def _get_sort_pos_of_custom_group(group: str) -> int:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    relevant_letter = group.replace("http://www.knora.org/ontology/knora-admin#", "")[0]
    return alphabet.index(relevant_letter.lower()) + 99  # must be higher than the highest index of the builtin groups


def sort_groups(groups_original: list[str]) -> list[str]:
    """Sorts groups, first according to their power (most powerful first), then alphabetically."""
    sort_key = [
        builtin_groups.SYSTEM_ADMIN, 
        builtin_groups.CREATOR, 
        builtin_groups.PROJECT_ADMIN, 
        builtin_groups.PROJECT_MEMBER, 
        builtin_groups.KNOWN_USER, 
        builtin_groups.UNKNOWN_USER
    ]
    groups = groups_original.copy()
    groups.sort(key=lambda x: sort_key.index(x) if x in sort_key else _get_sort_pos_of_custom_group(x))
    return groups
