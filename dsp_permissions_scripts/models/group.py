from __future__ import annotations

import re
from typing import Any
from typing import Protocol
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.utils.dsp_client import DspClient

KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"


class Group(Protocol):
    val: str

    def full_iri(self) -> str:
        pass


class BuiltinGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    val: str

    @model_validator(mode="before")
    @classmethod
    def _shorten_iri(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        data["val"] = data["val"].replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
        return data

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not self.val.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.val} is not a valid group IRI")
        return self

    def full_iri(self) -> str:
        return self.val.replace("knora-admin:", KNORA_ADMIN_ONTO_NAMESPACE)


class CustomGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str
    full_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not re.search(r"^\w+:\w+$", self.prefixed_iri):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid group IRI")
        return self

    @staticmethod
    def from_unprefixed_groupname(string: str, dsp_client: DspClient, shortcode: str) -> CustomGroup:
        all_groups = dsp_client.get("/admin/groups")["groups"]
        proj_groups = [grp for grp in all_groups if grp["project"]["shortcode"] == shortcode]
        group = [grp for grp in proj_groups if grp["name"] == string]
        if not group:
            msg = f"{string} is not a valid group. Available groups: {', '.join([grp['name'] for grp in proj_groups])}"
            raise InvalidGroupError(msg)
        prefixed_iri = f"{group[0]["project"]["shortname"]}:{string}"
        return CustomGroup(prefixed_iri=prefixed_iri, full_iri=group[0]["id"])


UNKNOWN_USER = BuiltinGroup(val="knora-admin:UnknownUser")
KNOWN_USER = BuiltinGroup(val="knora-admin:KnownUser")
PROJECT_MEMBER = BuiltinGroup(val="knora-admin:ProjectMember")
PROJECT_ADMIN = BuiltinGroup(val="knora-admin:ProjectAdmin")
CREATOR = BuiltinGroup(val="knora-admin:Creator")
SYSTEM_ADMIN = BuiltinGroup(val="knora-admin:SystemAdmin")
