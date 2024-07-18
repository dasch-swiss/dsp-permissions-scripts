from typing import Iterable

from dsp_permissions_scripts.models import group

PACKAGE_NAME = "dsp-permissions-scripts"
KNORA_ADMIN_ONTO_PREFIX = "http://www.knora.org/ontology/knora-admin#"


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


def shorten_iri_by_prefixing(
    iri: str,
    context: dict[str, str],
) -> str:
    """
    Transforms a full IRI into its shortened form, using the namespace prefix from the provided context.

    Args:
        iri: an full IRI, e.g. "http://www.knora.org/ontology/knora-admin#Creator"
        context: The context to use take the namespace prefix from

    Returns:
        The prefixed short form of the IRI, e.g. "knora-admin:Creator"
    """
    for namespace_prefix, full_iri in context.items():
        if iri.startswith(full_iri):
            return f"{namespace_prefix}:{iri[len(full_iri):]}"
    raise ValueError(f"Could not find a prefix for IRI {iri}")


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
