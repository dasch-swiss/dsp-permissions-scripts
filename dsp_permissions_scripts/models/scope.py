from pydantic import BaseModel

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScope(BaseModel):
    CR: list[str | BuiltinGroup] | None = None
    D: list[str | BuiltinGroup] | None = None
    M: list[str | BuiltinGroup] | None = None
    V: list[str | BuiltinGroup] | None = None
    RV: list[str | BuiltinGroup] | None = None


class StandardScope:
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions on a resource/value?"
    This class offers some predefined scopes.
    If your preferred scope is not available,
    please add a new class attribute and implement it in the __init__ method.
    """

    PUBLIC: PermissionScope

    def __init__(self):
        self.PUBLIC = PermissionScope(
            CR=[BuiltinGroup.PROJECT_ADMIN],
            D=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER],
            V=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
        )
