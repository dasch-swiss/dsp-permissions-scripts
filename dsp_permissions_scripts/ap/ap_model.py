from enum import Enum

from pydantic import BaseModel

from dsp_permissions_scripts.models.group import Group


class ApValue(Enum):
    # is allowed to create resources inside the project
    ProjectResourceCreateAllPermission = "ProjectResourceCreateAllPermission"
    # is allowed to create resources of certain classes inside the project
    ProjectResourceCreateRestrictedPermission = "ProjectResourceCreateRestrictedPermission"
    # is allowed to do anything on project level
    ProjectAdminAllPermission = "ProjectAdminAllPermission"
    # is allowed to modify group info and group membership on all groups belonging to the project
    ProjectAdminGroupAllPermission = "ProjectAdminGroupAllPermission"
    # is allowed to modify group info and group membership on certain groups belonging to the project
    ProjectAdminGroupRestrictedPermission = "ProjectAdminGroupRestrictedPermission"
    # is allowed to change the permissions on all objects belonging to the project
    ProjectAdminRightsAllPermission = "ProjectAdminRightsAllPermission"


class Ap(BaseModel):
    """Represents an Administrative Permission"""

    forGroup: Group
    forProject: str
    hasPermissions: frozenset[ApValue]
    iri: str

    def add_permission(self, permission: ApValue) -> None:
        if permission in self.hasPermissions:
            raise ValueError(f"Permission {permission} is already in the AP")
        self.hasPermissions = self.hasPermissions.union({permission})

    def remove_permission(self, permission: ApValue) -> None:
        if permission not in self.hasPermissions:
            raise ValueError(f"Permission {permission} is not in the AP")
        self.hasPermissions = self.hasPermissions.difference({permission})
