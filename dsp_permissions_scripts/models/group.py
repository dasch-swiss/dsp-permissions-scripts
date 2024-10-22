from __future__ import annotations

import re
from typing import Any
from typing import Iterable
from typing import Self
from typing import TypeAlias
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Discriminator
from pydantic import Tag
from pydantic import model_validator
from typing_extensions import Annotated

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.utils.dsp_client import DspClient

NAMES_OF_BUILTIN_GROUPS = ["SystemAdmin", "Creator", "ProjectAdmin", "ProjectMember", "KnownUser", "UnknownUser"]
KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"
PREFIXED_IRI_REGEX = r"^[\w-]+:[\w -]+$"


def is_prefixed_group_iri(iri: str) -> bool:
    if iri.startswith((KNORA_ADMIN_ONTO_NAMESPACE, "http://rdfh.ch/groups/", "knora-base:", "knora-api:")):
        return False
    elif iri.startswith("knora-admin:") and not iri.endswith(tuple(NAMES_OF_BUILTIN_GROUPS)):
        return False
    elif re.search(PREFIXED_IRI_REGEX, iri):
        return True
    else:
        raise InvalidIRIError(f"{iri} is not a valid group IRI")


def get_prefixed_iri_from_full_iri(full_iri: str, dsp_client: DspClient) -> str:
    if full_iri.startswith(KNORA_ADMIN_ONTO_NAMESPACE) and full_iri.endswith(tuple(NAMES_OF_BUILTIN_GROUPS)):
        return full_iri.replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
    elif full_iri.startswith("http://rdfh.ch/groups/"):
        all_groups = dsp_client.get("/admin/groups")["groups"]
        if not (group := [grp for grp in all_groups if grp["id"] == full_iri]):
            raise InvalidGroupError(
                f"{full_iri} is not a valid full IRI of a group. "
                f"Available group IRIs: {', '.join([grp['id'] for grp in all_groups])}"
            )
        return f"{group[0]["project"]["shortname"]}:{group[0]["name"]}"
    else:
        raise InvalidIRIError(f"Could not transform full IRI {full_iri} to prefixed IRI")


def get_full_iri_from_prefixed_iri(prefixed_iri: str, dsp_client: DspClient) -> str:
    if not is_prefixed_group_iri(prefixed_iri):
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
    proj_groups = [grp for grp in all_groups if grp["project"]["shortname"] == prefix]
    if not (group := [grp for grp in proj_groups if grp["name"] == groupname]):
        raise InvalidGroupError(
            f"{prefix}:{groupname} is not a valid group. "
            f"Available groups for the project {prefix}: {', '.join([grp['name'] for grp in proj_groups])}"
        )
    full_iri: str = group[0]["id"]
    return full_iri


def group_builder(prefixed_iri: str) -> BuiltinGroup | CustomGroup:
    if prefixed_iri.startswith("knora-admin:"):
        return BuiltinGroup(prefixed_iri=prefixed_iri)
    elif re.search(PREFIXED_IRI_REGEX, prefixed_iri):
        return CustomGroup(prefixed_iri=prefixed_iri)
    else:
        raise InvalidGroupError(f"{prefixed_iri} is not a valid group IRI")


class BuiltinGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        valid_group_names = ["SystemAdmin", "Creator", "ProjectAdmin", "ProjectMember", "KnownUser", "UnknownUser"]
        prefix, name = self.prefixed_iri.split(":")
        if prefix != "knora-admin" or name not in valid_group_names:
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        return self


class CustomGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not is_prefixed_group_iri(self.prefixed_iri):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        if self.prefixed_iri.startswith(("knora-admin:", "knora-base:", "knora-api:")):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a custom group")
        return self


def group_discriminator(v: Any) -> str:
    if isinstance(v, dict):
        return "builtin" if v["prefixed_iri"].startswith("knora-admin:") else "custom"
    else:
        return "builtin" if getattr(v, "prefixed_iri").startswith("knora-admin:") else "custom"


GroupType: TypeAlias = Annotated[
    Union[
        Annotated[BuiltinGroup, Tag("builtin")],
        Annotated[CustomGroup, Tag("custom")],
    ],
    Discriminator(group_discriminator),
]


def _get_sort_pos_of_custom_group(prefixed_iri: str) -> int:
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    relevant_letter = prefixed_iri.split(":")[-1][0]
    return alphabet.index(relevant_letter.lower()) + 99  # must be higher than the highest index of the builtin groups


def sort_groups(groups_original: Iterable[GroupType]) -> list[GroupType]:
    """
    Sorts groups:
     - First according to their power (most powerful first - only applicable for built-in groups)
     - Then alphabetically (custom groups)
    """
    sort_key = [SYSTEM_ADMIN, CREATOR, PROJECT_ADMIN, PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER]
    groups = list(groups_original)
    groups.sort(
        key=lambda x: sort_key.index(x)
        if isinstance(x, BuiltinGroup)
        else _get_sort_pos_of_custom_group(x.prefixed_iri)
    )
    return groups


UNKNOWN_USER = BuiltinGroup(prefixed_iri="knora-admin:UnknownUser")
KNOWN_USER = BuiltinGroup(prefixed_iri="knora-admin:KnownUser")
PROJECT_MEMBER = BuiltinGroup(prefixed_iri="knora-admin:ProjectMember")
PROJECT_ADMIN = BuiltinGroup(prefixed_iri="knora-admin:ProjectAdmin")
CREATOR = BuiltinGroup(prefixed_iri="knora-admin:Creator")
SYSTEM_ADMIN = BuiltinGroup(prefixed_iri="knora-admin:SystemAdmin")
