import re
from pydantic import BaseModel, model_validator


class Group(BaseModel):
    val: str

    @model_validator(mode="after")
    def _check_regex(self):
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
