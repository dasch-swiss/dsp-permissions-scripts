from __future__ import annotations

import re
from typing import Protocol
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.utils.dsp_client import DspClient

KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"


class Group(Protocol):
    prefixed_iri: str
    full_iri: str


class BuiltinGroup(BaseModel, Group):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str
    full_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not self.prefixed_iri.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid prefixed group IRI")
        if not self.full_iri.startswith(KNORA_ADMIN_ONTO_NAMESPACE):
            raise InvalidGroupError(f"{self.full_iri} is not a valid full group IRI")
        return self

    @staticmethod
    def from_full_iri(full_iri: str) -> BuiltinGroup:
        prefixed_iri = full_iri.replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
        return BuiltinGroup(prefixed_iri=prefixed_iri, full_iri=full_iri)

    @staticmethod
    def from_prefixed_iri(prefixed_iri: str) -> BuiltinGroup:
        full_iri = prefixed_iri.replace("knora-admin:", KNORA_ADMIN_ONTO_NAMESPACE)
        return BuiltinGroup(prefixed_iri=prefixed_iri, full_iri=full_iri)


class CustomGroup(BaseModel, Group):
    model_config = ConfigDict(frozen=True)

    prefixed_iri: str
    full_iri: str

    @model_validator(mode="after")
    def _check_regex(self) -> Self:
        if not re.search(r"^\w+:\w+$", self.prefixed_iri):
            raise InvalidGroupError(f"{self.prefixed_iri} is not a valid prefixed group IRI")
        if not re.search(r"http://rdfh.ch/groups/[0-9A-Fa-f]{4}/thing-searcher", self.full_iri):
            raise InvalidGroupError(f"{self.full_iri} is not a valid full group IRI")
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


UNKNOWN_USER = BuiltinGroup.from_prefixed_iri("knora-admin:UnknownUser")
KNOWN_USER = BuiltinGroup.from_prefixed_iri("knora-admin:KnownUser")
PROJECT_MEMBER = BuiltinGroup.from_prefixed_iri("knora-admin:ProjectMember")
PROJECT_ADMIN = BuiltinGroup.from_prefixed_iri("knora-admin:ProjectAdmin")
CREATOR = BuiltinGroup.from_prefixed_iri("knora-admin:Creator")
SYSTEM_ADMIN = BuiltinGroup.from_prefixed_iri("knora-admin:SystemAdmin")
