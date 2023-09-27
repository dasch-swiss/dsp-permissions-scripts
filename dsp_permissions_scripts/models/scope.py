from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import PermissionScope


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
