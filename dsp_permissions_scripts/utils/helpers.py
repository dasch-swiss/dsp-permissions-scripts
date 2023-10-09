from dsp_permissions_scripts.models.groups import BuiltinGroup


def dereference_prefix(
    identifier: str, 
    context: dict[str, str],
) -> str:
    prefix, actual_id = identifier.split(":")
    return context[prefix] + actual_id


def sort_algorith_custom_groups(group: str) -> int:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    relevant_letter = group.replace("http://www.knora.org/ontology/knora-admin#", "")[0]
    return alphabet.index(relevant_letter.lower()) + 999


def sort_groups(groups_original: list[str]) -> list[str]:
    """Sorts groups, first according to their power (most powerful first), then alphabetically."""
    sort_key = list(reversed([x.value for x in BuiltinGroup]))
    groups = groups_original.copy()
    groups.sort(key=lambda x: sort_key.index(x) if x in sort_key else sort_algorith_custom_groups(x))
    return groups
