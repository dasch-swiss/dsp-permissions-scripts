from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE

PREFIXED_IRI_REGEX = r"^[\w-]+:[\w -]+$"
NAMES_OF_BUILTIN_GROUPS = ["SystemAdmin", "Creator", "ProjectAdmin", "ProjectMember", "KnownUser", "UnknownUser"]


class Group(BaseModel):
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
    def _check_regex(self) -> Group:
        if not self.prefixed_iri.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        return self


def is_prefixed_group_iri(iri: str) -> bool:
    if iri.startswith((KNORA_ADMIN_ONTO_NAMESPACE, "http://rdfh.ch/groups/", "knora-base:", "knora-api:")):
        return False
    elif iri.startswith("knora-admin:") and not iri.endswith(tuple(NAMES_OF_BUILTIN_GROUPS)):
        return False
    elif re.search(PREFIXED_IRI_REGEX, iri):
        return True
    else:
        raise InvalidIRIError(f"{iri} is not a valid group IRI")


UNKNOWN_USER = Group(prefixed_iri="knora-admin:UnknownUser")
KNOWN_USER = Group(prefixed_iri="knora-admin:KnownUser")
PROJECT_MEMBER = Group(prefixed_iri="knora-admin:ProjectMember")
PROJECT_ADMIN = Group(prefixed_iri="knora-admin:ProjectAdmin")
CREATOR = Group(prefixed_iri="knora-admin:Creator")
SYSTEM_ADMIN = Group(prefixed_iri="knora-admin:SystemAdmin")
