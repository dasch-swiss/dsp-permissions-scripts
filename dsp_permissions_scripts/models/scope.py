from pydantic import BaseModel

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScope(BaseModel):
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions on a resource/value?"
    """

    CR: list[str | BuiltinGroup] = []
    D: list[str | BuiltinGroup] = []
    M: list[str | BuiltinGroup] = []
    V: list[str | BuiltinGroup] = []
    RV: list[str | BuiltinGroup] = []


PUBLIC = PermissionScope(
    CR=[BuiltinGroup.PROJECT_ADMIN],
    D=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER],
    V=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
)
