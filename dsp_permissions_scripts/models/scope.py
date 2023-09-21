from typing import Sequence

from dsp_permissions_scripts.models.groups import Group
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
            view=[Group.UNKNOWN_USER, Group.KNOWN_USER],
            change_rights=[Group.PROJECT_ADMIN],
            delete=[Group.CREATOR, Group.PROJECT_MEMBER],
        )

    def _make_scope(
        self,
        restricted_view: Sequence[str | Group] = (),
        view: Sequence[str | Group] = (),
        modify: Sequence[str | Group] = (),
        delete: Sequence[str | Group] = (),
        change_rights: Sequence[str | Group] = (),
    ) -> list[PermissionScopeElement]:
        """
        Create scopes by providing group IRIs for different permission levels.
        Every parameter represents the groups that get the corresponding permission.
        """
        perm_codes_to_groups = {"RV": restricted_view, "V": view, "M": modify, "D": delete, "CR": change_rights}
        res = []
        for perm_code, groups in perm_codes_to_groups.items():
            res.extend(
                [PermissionScopeElement(info=x if isinstance(x, str) else x.value, name=perm_code) for x in groups]
            )
        return res
