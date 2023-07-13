from typing import Sequence
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import PermissionScope


class StandardScope:
    """
    A scope is an object encoding the information: which user group gets which permissions, if a certain DOAP gets applied.
    This class offers some predefined scopes.
    If your preferred scope is not available,
    please add a new class variable and implement it in the __init__ method.
    """
    PUBLIC: list[PermissionScope]    
    
    def __init__(self):
        self.PUBLIC = self._make_scope(
            view=[BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER],
            change_rights=[BuiltinGroup.PROJECT_ADMIN],
            delete=[BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER]
        )

    def _make_scope(
        self,
        restricted_view: Sequence[str] = (),
        view: Sequence[str] = (),
        modify: Sequence[str] = (),
        delete: Sequence[str] = (),
        change_rights: Sequence[str] = ()
    ) -> list[PermissionScope]:
        """
        Helper method to create scopes, by providing lists of Group IRIs for different permission levels.
        """
        res = []
        res.extend([PermissionScope(info=iri, name="RV") for iri in restricted_view])
        res.extend([PermissionScope(info=iri, name="V") for iri in view])
        res.extend([PermissionScope(info=iri, name="M") for iri in modify])
        res.extend([PermissionScope(info=iri, name="D") for iri in delete])
        res.extend([PermissionScope(info=iri, name="CR") for iri in change_rights])
        return res
