import re
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, model_validator


@runtime_checkable
class Group(Protocol):
    value: str


class BuiltinGroup(Enum):
    """Enumeration of the built in DSP user groups."""

    UNKNOWN_USER = "http://www.knora.org/ontology/knora-admin#UnknownUser"
    KNOWN_USER = "http://www.knora.org/ontology/knora-admin#KnownUser"
    PROJECT_MEMBER = "http://www.knora.org/ontology/knora-admin#ProjectMember"
    PROJECT_ADMIN = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
    CREATOR = "http://www.knora.org/ontology/knora-admin#Creator"
    SYSTEM_ADMIN = "http://www.knora.org/ontology/knora-admin#SystemAdmin"


class CustomGroup(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    value: str

    @model_validator(mode="after")
    def check_group_is_iri(self):
        if not re.search(r"http:\/\/rdfh\.ch\/groups/[0-9a-f]{4}", self.value, flags=re.IGNORECASE):
            raise ValueError(f"Group '{self.value}' is not a DSP group IRI")
        if re.search(r"http:\/\/www\.knora\.org\/ontology\/knora-admin#", self.value, flags=re.IGNORECASE):
            raise ValueError(f"Group '{self.value}' is a built-in group IRI")
        return self
