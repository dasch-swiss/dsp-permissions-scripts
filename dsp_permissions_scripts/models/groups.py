from enum import Enum

class BuiltinGroup(Enum):
    """
    Enumeration of the built in DSP user groups.
    """
    UNKNOWN_USER = "http://www.knora.org/ontology/knora-admin#UnknownUser"
    KNOWN_USER = "http://www.knora.org/ontology/knora-admin#KnownUser"
    CREATOR = "http://www.knora.org/ontology/knora-admin#Creator"
    PROJECT_MEMBER = "http://www.knora.org/ontology/knora-admin#ProjectMember"
    PROJECT_ADMIN = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
    SYSTEM_ADMIN = "http://www.knora.org/ontology/knora-admin#SystemAdmin"
