from __future__ import annotations

import copy
from typing import Iterable
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import Group


class PermissionScope(BaseModel):
    """A scope is an object encoding the information: Which user group gets which permissions on a resource/value?"""

    model_config = ConfigDict(frozen=True)

    CR: frozenset[Group] = frozenset()
    D: frozenset[Group] = frozenset()
    M: frozenset[Group] = frozenset()
    V: frozenset[Group] = frozenset()
    RV: frozenset[Group] = frozenset()

    @staticmethod
    def create(
        CR: Iterable[Group] = (),
        D: Iterable[Group] = (),
        M: Iterable[Group] = (),
        V: Iterable[Group] = (),
        RV: Iterable[Group] = (),
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
    def from_dict(d: dict[str, list[str]]) -> PermissionScope:
        purged_kwargs = PermissionScope._remove_duplicates_from_kwargs(d)
        return PermissionScope.model_validate({k: [Group(val=v) for v in vs] for k, vs in purged_kwargs.items()})

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
            all_groups.extend([g.val for g in self.get(field)])
        for group in all_groups:
            if all_groups.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self

    def get(self, permission: str) -> frozenset[Group]:
        """Retrieve the groups that have the given permission."""
        if permission not in self.model_fields:
            raise ValueError(f"Permission '{permission}' not in {self.model_fields}")
        res: frozenset[Group] = getattr(self, permission)
        return res

    def add(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: Group,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group added to permission."""
        groups = self.get(permission)
        if group.val in [g.val for g in groups]:
            raise ValueError(f"Group '{group}' is already in permission '{permission}'")
        groups = groups | {group}
        kwargs: dict[str, frozenset[Group]] = {permission: groups}
        for perm in self.model_fields:
            if perm != permission:
                kwargs[perm] = self.get(perm)
        return PermissionScope.create(**kwargs)

    def remove(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: Group,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group removed from permission."""
        groups = self.get(permission)
        if group.val not in [g.val for g in groups]:
            raise ValueError(f"Group '{group}' is not in permission '{permission}'")
        groups = groups - {group}
        kwargs: dict[str, frozenset[Group]] = {permission: groups}
        for perm in self.model_fields:
            if perm != permission:
                kwargs[perm] = self.get(perm)
        return PermissionScope.create(**kwargs)


PUBLIC = PermissionScope.create(
    CR={PROJECT_ADMIN},
    D={CREATOR, PROJECT_MEMBER},
    V={UNKNOWN_USER, KNOWN_USER},
)

PRIVATE = PermissionScope.create(
    CR={PROJECT_ADMIN, CREATOR},
    V={PROJECT_MEMBER},
)
