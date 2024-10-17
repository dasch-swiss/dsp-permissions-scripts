from __future__ import annotations

from typing import Any
from typing import Protocol

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import InvalidGroupError

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
    def _check_regex(self) -> BuiltinGroup:
        if not self.val.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.val} is not a valid group IRI")
        return self

    def full_iri(self) -> str:
        return self.val.replace("knora-admin:", KNORA_ADMIN_ONTO_NAMESPACE)


UNKNOWN_USER = BuiltinGroup(val="knora-admin:UnknownUser")
KNOWN_USER = BuiltinGroup(val="knora-admin:KnownUser")
PROJECT_MEMBER = BuiltinGroup(val="knora-admin:ProjectMember")
PROJECT_ADMIN = BuiltinGroup(val="knora-admin:ProjectAdmin")
CREATOR = BuiltinGroup(val="knora-admin:Creator")
SYSTEM_ADMIN = BuiltinGroup(val="knora-admin:SystemAdmin")
