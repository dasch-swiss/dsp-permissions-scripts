from __future__ import annotations

import re
from typing import Any
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
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE

PREFIXED_IRI_REGEX = r"^[\w-]+:[\w -]+$"
NAMES_OF_BUILTIN_GROUPS = ["SystemAdmin", "Creator", "ProjectAdmin", "ProjectMember", "KnownUser", "UnknownUser"]


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
        if not is_valid_prefixed_group_iri(self.prefixed_iri):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        if self.prefixed_iri.startswith(("knora-admin:", "knora-base:", "knora-api:")):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a custom group")
        return self


def group_builder(prefixed_iri: str) -> BuiltinGroup | CustomGroup:
    if prefixed_iri.startswith("knora-admin:"):
        return BuiltinGroup(prefixed_iri=prefixed_iri)
    elif re.search(PREFIXED_IRI_REGEX, prefixed_iri):
        return CustomGroup(prefixed_iri=prefixed_iri)
    else:
        raise InvalidGroupError(f"{prefixed_iri} is not a valid group IRI")


def group_discriminator(v: Any) -> str:
    if isinstance(v, dict):
        return "builtin" if v["prefixed_iri"].startswith("knora-admin:") else "custom"
    else:
        return "builtin" if getattr(v, "prefixed_iri").startswith("knora-admin:") else "custom"


Group: TypeAlias = Annotated[
    Union[
        Annotated[BuiltinGroup, Tag("builtin")],
        Annotated[CustomGroup, Tag("custom")],
    ],
    Discriminator(group_discriminator),
]


def is_valid_prefixed_group_iri(iri: str) -> bool:
    if iri.startswith((KNORA_ADMIN_ONTO_NAMESPACE, "http://rdfh.ch/groups/", "knora-base:", "knora-api:")):
        return False
    elif iri.startswith("knora-admin:") and not iri.endswith(tuple(NAMES_OF_BUILTIN_GROUPS)):
        return False
    elif re.search(PREFIXED_IRI_REGEX, iri):
        return True
    else:
        return False


UNKNOWN_USER = BuiltinGroup(prefixed_iri="knora-admin:UnknownUser")
KNOWN_USER = BuiltinGroup(prefixed_iri="knora-admin:KnownUser")
PROJECT_MEMBER = BuiltinGroup(prefixed_iri="knora-admin:ProjectMember")
PROJECT_ADMIN = BuiltinGroup(prefixed_iri="knora-admin:ProjectAdmin")
CREATOR = BuiltinGroup(prefixed_iri="knora-admin:Creator")
SYSTEM_ADMIN = BuiltinGroup(prefixed_iri="knora-admin:SystemAdmin")
