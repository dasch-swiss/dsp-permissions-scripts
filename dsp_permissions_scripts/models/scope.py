from __future__ import annotations

import copy
from typing import Iterable
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import EmptyScopeError
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import GroupType
from dsp_permissions_scripts.models.group import get_prefixed_iri_from_full_iri
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.group import is_prefixed_iri
from dsp_permissions_scripts.utils.dsp_client import DspClient


class PermissionScope(BaseModel):
    """A scope is an object encoding the information: Which user group gets which permissions on a resource/value?"""

    model_config = ConfigDict(frozen=True)

    CR: frozenset[GroupType] = frozenset()
    D: frozenset[GroupType] = frozenset()
    M: frozenset[GroupType] = frozenset()
    V: frozenset[GroupType] = frozenset()
    RV: frozenset[GroupType] = frozenset()

    @staticmethod
    def create(
        CR: Iterable[GroupType] = (),
        D: Iterable[GroupType] = (),
        M: Iterable[GroupType] = (),
        V: Iterable[GroupType] = (),
        RV: Iterable[GroupType] = (),
    ) -> PermissionScope:
        """Factory method to create a PermissionScope from Iterables instead of frozensets."""
        return PermissionScope(
            CR=frozenset(CR),
            D=frozenset(D),
            M=frozenset(M),
            V=frozenset(V),
            RV=frozenset(RV),
        )

    @staticmethod
    def from_dict(d: dict[str, list[str]], dsp_client: DspClient) -> PermissionScope:
        purged_kwargs = PermissionScope._remove_duplicates_from_kwargs(d)
        purged_kwargs_final = {}
        for k, vs in purged_kwargs.items():
            groups = []
            for v in vs:
                if is_prefixed_iri(v):
                    groups.append(group_builder(v))
                else:
                    groups.append(group_builder(get_prefixed_iri_from_full_iri(v, dsp_client)))
            purged_kwargs_final[k] = groups
        return PermissionScope.model_validate(purged_kwargs_final)

    @staticmethod
    def _remove_duplicates_from_kwargs(kwargs: dict[str, list[str]]) -> dict[str, list[str]]:
        res = copy.deepcopy(kwargs)
        permissions = ["RV", "V", "M", "D", "CR"]
        permissions = [perm for perm in permissions if perm in kwargs]
        for perm in permissions:
            higher_permissions = permissions[permissions.index(perm) + 1 :] if perm != "CR" else []
            for group in kwargs[perm]:
                nested_list = [kwargs[hp] for hp in higher_permissions]
                flat_list = [y for x in nested_list for y in x]
                if flat_list.count(group) > 0:
                    res[perm].remove(group)
        return res

    @model_validator(mode="after")
    def check_group_occurs_only_once(self) -> PermissionScope:
        all_groups = []
        for field in self.model_fields:
            all_groups.extend([g.prefixed_iri for g in self.get(field)])
        for group in all_groups:
            if all_groups.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self

    @model_validator(mode="after")
    def check_scope_not_empty(self) -> PermissionScope:
        if not any([len(self.get(field)) > 0 for field in self.model_fields]):
            raise EmptyScopeError()
        return self

    def get(self, permission: str) -> frozenset[GroupType]:
        """Retrieve the groups that have the given permission."""
        if permission not in self.model_fields:
            raise ValueError(f"Permission '{permission}' not in {self.model_fields}")
        res: frozenset[GroupType] = getattr(self, permission)
        return res

    def add(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: GroupType,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group added to permission."""
        groups = self.get(permission)
        if group.prefixed_iri in [g.prefixed_iri for g in groups]:
            raise ValueError(f"Group '{group}' is already in permission '{permission}'")
        groups = groups | {group}
        kwargs: dict[str, frozenset[GroupType]] = {permission: groups}
        for perm in self.model_fields:
            if perm != permission:
                kwargs[perm] = self.get(perm)
        return PermissionScope.create(**kwargs)

    def remove(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: GroupType,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group removed from permission."""
        groups = self.get(permission)
        if group.prefixed_iri not in [g.prefixed_iri for g in groups]:
            raise ValueError(f"Group '{group}' is not in permission '{permission}'")
        groups = groups - {group}
        kwargs: dict[str, frozenset[GroupType]] = {permission: groups}
        for perm in self.model_fields:
            if perm != permission:
                kwargs[perm] = self.get(perm)
        return PermissionScope.create(**kwargs)


OPEN = PermissionScope.create(
    CR=[PROJECT_ADMIN],
    D=[PROJECT_MEMBER],
    V=[KNOWN_USER, UNKNOWN_USER],
)

RESTRICTED_VIEW = PermissionScope.create(
    CR=[PROJECT_ADMIN],
    D=[PROJECT_MEMBER],
    RV=[KNOWN_USER, UNKNOWN_USER],
)

RESTRICTED = PermissionScope.create(
    CR=[PROJECT_ADMIN],
    D=[PROJECT_MEMBER],
)

LIMC_OPEN = PermissionScope.create(
    CR=[PROJECT_ADMIN],
    D=[group_builder("limc:limc-editors")],
    V=[PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER],
)
