from typing import Sequence

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import PermissionScopeElement


class StandardScope:
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions, if a certain DOAP gets applied?"
    This class offers some predefined scopes.
    If your preferred scope is not available,
    please add a new class variable and implement it in the __init__ method.
    """

    PUBLIC: list[PermissionScopeElement]

    def __init__(self):
        self.PUBLIC = self._make_scope(
            view=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
            change_rights=[BuiltinGroup.PROJECT_ADMIN],
            delete=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER],
        )

    def _make_scope(
        self,
        restricted_view: Sequence[str | BuiltinGroup] = (),
        view: Sequence[str | BuiltinGroup] = (),
        modify: Sequence[str | BuiltinGroup] = (),
        delete: Sequence[str | BuiltinGroup] = (),
        change_rights: Sequence[str | BuiltinGroup] = (),
    ) -> list[PermissionScopeElement]:
        """
        Create scopes by providing group IRIs for different permission levels.
        Every parameter represents the groups that get the corresponding permission.
        """
        perm_codes_to_groups = {"RV": restricted_view, "V": view, "M": modify, "D": delete, "CR": change_rights}
        res = []
        for perm_code, groups in perm_codes_to_groups.items():
            res.extend(
                [PermissionScopeElement(group_iri=x if isinstance(x, str) else x.value, permission_code=perm_code) for x in groups]
            )
        return res
