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
from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.group import is_valid_group_iri
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE


def sort_groups(groups_original: Iterable[Group]) -> list[Group]:
    """
    Sorts groups:
     - First according to their power (most powerful first - only applicable for built-in groups)
     - Then alphabetically (custom groups)
    """
    builtin_order = [SYSTEM_ADMIN, CREATOR, PROJECT_ADMIN, PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER]

    builtin_groups: list[BuiltinGroup] = []
    custom_groups: list[CustomGroup] = []

    for group in groups_original:
        match group:
            case BuiltinGroup():
                builtin_groups.append(group)
            case CustomGroup():
                custom_groups.append(group)

    builtin_groups.sort(key=lambda x: builtin_order.index(x))
    custom_groups.sort(key=lambda x: x.prefixed_iri.lower())

    return builtin_groups + custom_groups


def get_prefixed_iri_from_full_iri(full_iri: str, dsp_client: DspClient) -> str:
    if full_iri.startswith(KNORA_ADMIN_ONTO_NAMESPACE) and full_iri.endswith(tuple(NAMES_OF_BUILTIN_GROUPS)):
        return full_iri.replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
    elif full_iri.startswith("http://rdfh.ch/groups/"):
        all_groups = dsp_client.get("/admin/groups")["groups"]
        if not (group := [grp for grp in all_groups if grp["id"].casefold() == full_iri.casefold()]):
            raise InvalidGroupError(
                f"{full_iri} is not a valid full IRI of a group. "
                f"Available group IRIs: {', '.join([grp['id'] for grp in all_groups])}"
            )
        return f"{group[0]["project"]["shortname"]}:{group[0]["name"]}"
    else:
        raise InvalidIRIError(f"Could not transform full IRI {full_iri} to prefixed IRI")


def get_full_iri_from_prefixed_iri(prefixed_iri: str, dsp_client: DspClient) -> str:
    if not is_valid_group_iri(prefixed_iri):
        raise InvalidIRIError(f"{prefixed_iri} is not a valid prefixed group IRI")
    prefix, groupname = prefixed_iri.split(":")
    if prefix == "knora-admin":
        return _get_full_iri_from_builtin_group(prefix, groupname)
    else:
        return _get_full_iri_from_custom_group(prefix, groupname, dsp_client)


def _get_full_iri_from_builtin_group(prefix: str, groupname: str) -> str:
    if groupname not in NAMES_OF_BUILTIN_GROUPS:
        raise InvalidGroupError(f"{prefix}:{groupname} is not a valid builtin group")
    return f"{KNORA_ADMIN_ONTO_NAMESPACE}{groupname}"


def _get_full_iri_from_custom_group(prefix: str, groupname: str, dsp_client: DspClient) -> str:
    all_groups = dsp_client.get("/admin/groups")["groups"]
    proj_groups = [grp for grp in all_groups if grp["project"]["shortname"].casefold() == prefix.casefold()]
    if not (group := [grp for grp in proj_groups if grp["name"] == groupname]):
        raise InvalidGroupError(
            f"{prefix}:{groupname} is not a valid group. "
            f"Available groups for the project {prefix}: {', '.join([grp['name'] for grp in proj_groups])}"
        )
    full_iri: str = group[0]["id"]
    return full_iri
