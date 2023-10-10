from __future__ import annotations

from typing import Iterable, Literal

from pydantic import BaseModel, ConfigDict, model_validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScope(BaseModel):
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions on a resource/value?"
    """
    model_config = ConfigDict(frozen=True)

    CR: frozenset[str | BuiltinGroup] = frozenset()
    D: frozenset[str | BuiltinGroup] = frozenset()
    M: frozenset[str | BuiltinGroup] = frozenset()
    V: frozenset[str | BuiltinGroup] = frozenset()
    RV: frozenset[str | BuiltinGroup] = frozenset()

    @staticmethod
    def create(
        CR: Iterable[str | BuiltinGroup] = (),
        D: Iterable[str | BuiltinGroup] = (),
        M: Iterable[str | BuiltinGroup] = (),
        V: Iterable[str | BuiltinGroup] = (),
        RV: Iterable[str | BuiltinGroup] = (),
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
        all_groups_as_strs = [g.value if isinstance(g, BuiltinGroup) else g for g in all_groups]
        for group in all_groups_as_strs:
            if all_groups_as_strs.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self

    def add(
        self,
        permission: Literal["CR", "D", "M", "V", "RV"],
        group: str | BuiltinGroup,
    ) -> PermissionScope:
        """Return a copy of the PermissionScope instance with group added to permission."""
        groups = [g.value if isinstance(g, BuiltinGroup) else g for g in getattr(self, permission)]
        group = group.value if isinstance(group, BuiltinGroup) else group
        if group in groups:
            raise ValueError(f"Group '{group}' is already in permission '{permission}'")
        groups.append(group)
        kwargs: dict[str, list[str]] = {permission: groups}
        for perm in ["CR", "D", "M", "V", "RV"]:
            if perm != permission:
                kwargs[perm] = getattr(self, perm)
        return PermissionScope.create(**kwargs)


PUBLIC = PermissionScope.create(
    CR={BuiltinGroup.PROJECT_ADMIN},
    D={BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER},
    V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
)
