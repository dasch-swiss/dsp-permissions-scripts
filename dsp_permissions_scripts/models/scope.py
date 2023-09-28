from enum import Enum

from pydantic import BaseModel

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScopeFields(Enum):
    CR = "change_rights"
    D = "delete"
    M = "modify"
    V = "view"
    RV = "restricted_view"


class PermissionScope(BaseModel):
    change_rights: list[str | BuiltinGroup] | None = None
    delete: list[str | BuiltinGroup] | None = None
    modify: list[str | BuiltinGroup] | None = None
    view: list[str | BuiltinGroup] | None = None
    restricted_view: list[str | BuiltinGroup] | None = None


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
            change_rights=[BuiltinGroup.PROJECT_ADMIN],
            delete=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER],
            view=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
        )
