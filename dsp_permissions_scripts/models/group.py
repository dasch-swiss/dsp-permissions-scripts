from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import InvalidGroupError


class Group(BaseModel):
    model_config = ConfigDict(frozen=True)

    val: str

    @model_validator(mode="after")
    def _check_regex(self) -> Group:
        if not self.val.startswith("knora-admin:"):
            raise InvalidGroupError(f"{self.val} is not a valid group IRI")
        return self


UNKNOWN_USER = Group(val="knora-admin:UnknownUser")
KNOWN_USER = Group(val="knora-admin:KnownUser")
PROJECT_MEMBER = Group(val="knora-admin:ProjectMember")
PROJECT_ADMIN = Group(val="knora-admin:ProjectAdmin")
CREATOR = Group(val="knora-admin:Creator")
SYSTEM_ADMIN = Group(val="knora-admin:SystemAdmin")
