from __future__ import annotations

from typing import Iterable, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from dsp_permissions_scripts.models.group import CREATOR, KNOWN_USER, PROJECT_ADMIN, PROJECT_MEMBER, UNKNOWN_USER, Group


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

    @model_validator(mode="after")
    def check_group_occurs_only_once(self) -> PermissionScope:
        all_groups: list[str] = []
        for field in self.model_fields:
            groups: frozenset[Group] = getattr(self, field)
            all_groups.extend([g.val for g in groups])
        for group in all_groups:
            if all_groups.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self

    def add(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: Group,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group added to permission."""
        groups: frozenset[Group] = getattr(self, permission)
        if group.val in [g.val for g in groups]:
            raise ValueError(f"Group '{group}' is already in permission '{permission}'")
        groups = groups | {group}
        kwargs: dict[str, frozenset[Group]] = {permission: groups}
        for perm in ["CR", "D", "M", "V", "RV"]:
            if perm != permission:
                kwargs[perm] = getattr(self, perm)
        return PermissionScope.create(**kwargs)

    def remove(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: Group,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group removed from permission."""
        groups: frozenset[Group] = getattr(self, permission)
        if group.val not in [g.val for g in groups]:
            raise ValueError(f"Group '{group}' is not in permission '{permission}'")
        groups = groups - {group}
        kwargs: dict[str, frozenset[Group]] = {permission: groups}
        for perm in ["CR", "D", "M", "V", "RV"]:
            if perm != permission:
                kwargs[perm] = getattr(self, perm)
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
