from pydantic import BaseModel

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScope(BaseModel):
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions on a resource/value?"
    """

    CR: set[str | BuiltinGroup] = set()
    D: set[str | BuiltinGroup] = set()
    M: set[str | BuiltinGroup] = set()
    V: set[str | BuiltinGroup] = set()
    RV: set[str | BuiltinGroup] = set()


PUBLIC = PermissionScope(
    CR={BuiltinGroup.PROJECT_ADMIN},
    D={BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER},
    V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
)
