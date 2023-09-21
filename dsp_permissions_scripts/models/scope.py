from typing import Sequence

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import PermissionScope


class StandardScope:
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions, if a certain DOAP gets applied?"
    This class offers some predefined scopes.
    If your preferred scope is not available,
    please add a new class variable and implement it in the __init__ method.
    """

    PUBLIC: list[PermissionScope]
    READ_ONLY_FOR_GROUP_SCENARIO_TANNER: list[PermissionScope]

    def __init__(self):
        self.PUBLIC = self._make_scope(
            view=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
            change_rights=[BuiltinGroup.PROJECT_ADMIN],
            delete=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER],
        )
        self.READ_ONLY_FOR_GROUP_SCENARIO_TANNER = self._make_scope(
            view=[],
            change_rights=[],
            delete=[],
        )

    def _make_scope(
        self,
        restricted_view: Sequence[str | BuiltinGroup] = (),
        view: Sequence[str | BuiltinGroup] = (),
        modify: Sequence[str | BuiltinGroup] = (),
        delete: Sequence[str | BuiltinGroup] = (),
        change_rights: Sequence[str | BuiltinGroup] = (),
    ) -> list[PermissionScope]:
        """
        Create scopes by providing group IRIs for different permission levels.
        """
        res = []
        res.extend([PermissionScope(info=x if isinstance(x, str) else x.value, name="RV") for x in restricted_view])
        res.extend([PermissionScope(info=x if isinstance(x, str) else x.value, name="V") for x in view])
        res.extend([PermissionScope(info=x if isinstance(x, str) else x.value, name="M") for x in modify])
        res.extend([PermissionScope(info=x if isinstance(x, str) else x.value, name="D") for x in delete])
        res.extend([PermissionScope(info=x if isinstance(x, str) else x.value, name="CR") for x in change_rights])
        return res
