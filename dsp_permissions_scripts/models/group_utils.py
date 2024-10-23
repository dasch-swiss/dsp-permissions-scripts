from typing import Iterable

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import NAMES_OF_BUILTIN_GROUPS
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.group import is_prefixed_group_iri
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE


def sort_groups(groups_original: Iterable[Group]) -> list[Group]:
    """
    Sorts groups:
     - First according to their power (most powerful first - only applicable for built-in groups)
     - Then alphabetically (custom groups)
    """
    sort_key = [SYSTEM_ADMIN, CREATOR, PROJECT_ADMIN, PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER]
    groups = list(groups_original)
    groups.sort(key=lambda x: sort_key.index(x) if x in sort_key else _get_sort_pos_of_custom_group(x.prefixed_iri))
    return groups


def _get_sort_pos_of_custom_group(group: str) -> int:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    relevant_letter = group.replace("knora-admin:", "")[0]
    return alphabet.index(relevant_letter.lower()) + 99  # must be higher than the highest index of the builtin groups


def get_full_iri_from_prefixed_iri(prefixed_iri: str) -> str:
    if not is_prefixed_group_iri(prefixed_iri):
        raise InvalidIRIError(f"{prefixed_iri} is not a valid prefixed group IRI")
    prefix, groupname = prefixed_iri.split(":")
    if prefix == "knora-admin":
        return _get_full_iri_from_builtin_group(prefix, groupname)
    raise NotImplementedError(
        f"Dereferencing custom group IRIs is not supported yet, hence {prefixed_iri} cannot be dereferenced"
    )


def _get_full_iri_from_builtin_group(prefix: str, groupname: str) -> str:
    if groupname not in NAMES_OF_BUILTIN_GROUPS:
        raise InvalidGroupError(f"{prefix}:{groupname} is not a valid builtin group")
    return f"{KNORA_ADMIN_ONTO_NAMESPACE}{groupname}"
