from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
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
from dsp_permissions_scripts.utils.dsp_client import DspClient

KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"


def group_builder(prefixed_or_full_iri: str) -> BuiltinGroup | CustomGroup:
    if prefixed_or_full_iri.startswith(KNORA_ADMIN_ONTO_NAMESPACE):
        prefixed_iri = prefixed_or_full_iri.replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
        return BuiltinGroup(prefixed_iri=prefixed_iri)
    elif prefixed_or_full_iri.startswith("knora-admin:"):
        return BuiltinGroup(prefixed_iri=prefixed_or_full_iri)
    return CustomGroup(prefixed_iri=prefixed_or_full_iri)


class Group(BaseModel, ABC):
    prefixed_iri: str

    @abstractmethod
    def full_iri(self, *args: Any) -> str: ...


class BuiltinGroup(Group):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str

    @model_validator(mode="before")
    @classmethod
    def _shorten_iri(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        data["prefixed_iri"] = data["prefixed_iri"].replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
        return data

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not self.prefixed_iri.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        return self

    def full_iri(self) -> str:
        return self.prefixed_iri.replace("knora-admin:", KNORA_ADMIN_ONTO_NAMESPACE)


class CustomGroup(Group):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not re.search(r"^.+:.+$", self.prefixed_iri):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        return self

    def full_iri(self, dsp_client: DspClient, shortcode: str) -> str:
        all_groups = dsp_client.get("/admin/groups")["groups"]
        proj_groups = [grp for grp in all_groups if grp["project"]["shortcode"] == shortcode]
        if not (group := [grp for grp in proj_groups if grp["name"] == self.prefixed_iri.split(":")[-1]]):
            raise InvalidGroupError(
                f"{self.prefixed_iri} is not a valid group. "
                "Available groups: {', '.join([grp['name'] for grp in proj_groups])}"
            )
        full_iri: str = group[0]["id"]
        return full_iri


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


def sort_groups(groups_original: Iterable[Group]) -> list[Group]:
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
