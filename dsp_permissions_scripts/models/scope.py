from __future__ import annotations

from typing import Iterable, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from dsp_permissions_scripts.models import builtin_groups


class PermissionScope(BaseModel):
    """A scope is an object encoding the information: Which user group gets which permissions on a resource/value?"""

    model_config = ConfigDict(frozen=True)

    CR: frozenset[str] = frozenset()
    D: frozenset[str] = frozenset()
    M: frozenset[str] = frozenset()
    V: frozenset[str] = frozenset()
    RV: frozenset[str] = frozenset()

    @staticmethod
    def create(
        CR: Iterable[str] = (),
        D: Iterable[str] = (),
        M: Iterable[str] = (),
        V: Iterable[str] = (),
        RV: Iterable[str] = (),
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
    def check_group_occurs_only_once(self):
        all_groups = []
        for field in self.model_fields:
            all_groups.extend(getattr(self, field))
        for group in all_groups:
            if all_groups.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self

    def add(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: str,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group added to permission."""
        groups = getattr(self, permission)
        if group in groups:
            raise ValueError(f"Group '{group}' is already in permission '{permission}'")
        groups = groups | {group}
        kwargs: dict[str, list[str]] = {permission: groups}
        for perm in ["CR", "D", "M", "V", "RV"]:
            if perm != permission:
                kwargs[perm] = getattr(self, perm)
        return PermissionScope.create(**kwargs)

    def remove(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: str,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group removed from permission."""
        groups = getattr(self, permission)
        if group not in groups:
            raise ValueError(f"Group '{group}' is not in permission '{permission}'")
        groups = groups - {group}
        kwargs: dict[str, list[str]] = {permission: groups}
        for perm in ["CR", "D", "M", "V", "RV"]:
            if perm != permission:
                kwargs[perm] = getattr(self, perm)
        return PermissionScope.create(**kwargs)


PUBLIC = PermissionScope.create(
    CR={builtin_groups.PROJECT_ADMIN},
    D={builtin_groups.CREATOR, builtin_groups.PROJECT_MEMBER},
    V={builtin_groups.UNKNOWN_USER, builtin_groups.KNOWN_USER},
)

PRIVATE = PermissionScope.create(
    CR={builtin_groups.PROJECT_ADMIN, builtin_groups.CREATOR},
    V={builtin_groups.PROJECT_MEMBER},
)
