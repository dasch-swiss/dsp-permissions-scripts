from __future__ import annotations

import re

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator


class Group(BaseModel):

    model_config = ConfigDict(frozen=True)
    
    val: str

    @model_validator(mode="after")
    def _check_regex(self) -> Group:
        common_part = re.escape("http://www.knora.org/ontology/knora-admin#")
        if not re.search(f"{common_part}.+", self.val):
            raise ValueError(f"{self.val} is not a valid group IRI")
        return self

UNKNOWN_USER = Group(val="http://www.knora.org/ontology/knora-admin#UnknownUser")
KNOWN_USER = Group(val="http://www.knora.org/ontology/knora-admin#KnownUser")
PROJECT_MEMBER = Group(val="http://www.knora.org/ontology/knora-admin#ProjectMember")
PROJECT_ADMIN = Group(val="http://www.knora.org/ontology/knora-admin#ProjectAdmin")
CREATOR = Group(val="http://www.knora.org/ontology/knora-admin#Creator")
SYSTEM_ADMIN = Group(val="http://www.knora.org/ontology/knora-admin#SystemAdmin")
