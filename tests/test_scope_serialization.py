import pytest
from pytest_unordered import unordered

from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.utils.scope_serialization import create_admin_route_object_from_scope
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_admin_route_object
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope


class TestScopeSerialization:
    perm_strings = (
        "CR knora-admin:SystemAdmin",
        "D knora-admin:ProjectAdmin|RV knora-admin:ProjectMember",
        "M knora-admin:ProjectAdmin|V knora-admin:Creator,knora-admin:KnownUser|RV knora-admin:UnknownUser",
        "CR knora-admin:SystemAdmin,knora-admin:ProjectAdmin|D knora-admin:Creator|RV knora-admin:UnknownUser",
    )
    admin_route_objects = (
        [
            {"name": "CR", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}SystemAdmin", "permissionCode": None},
        ],
        [
            {"name": "D", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin", "permissionCode": None},
            {
                "name": "RV",
                "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectMember",
                "permissionCode": None,
            },
        ],
        [
            {"name": "M", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin", "permissionCode": None},
            {"name": "V", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}Creator", "permissionCode": None},
            {"name": "V", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}KnownUser", "permissionCode": None},
            {"name": "RV", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}UnknownUser", "permissionCode": None},
        ],
        [
            {"name": "CR", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}SystemAdmin", "permissionCode": None},
            {
                "name": "CR",
                "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin",
                "permissionCode": None,
            },
            {"name": "D", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}Creator", "permissionCode": None},
            {"name": "RV", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}UnknownUser", "permissionCode": None},
        ],
    )
    scopes = (
        PermissionScope.create(
            CR=[SYSTEM_ADMIN],
        ),
        PermissionScope.create(
            D=[PROJECT_ADMIN],
            RV=[PROJECT_MEMBER],
        ),
        PermissionScope.create(
            M=[PROJECT_ADMIN],
            V=[CREATOR, KNOWN_USER],
            RV=[UNKNOWN_USER],
        ),
        PermissionScope.create(
            CR=[SYSTEM_ADMIN, PROJECT_ADMIN],
            D=[CREATOR],
            RV=[UNKNOWN_USER],
        ),
    )

    def test_create_scope_from_string(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            assert create_scope_from_string(perm_string) == scope, f"Failed with permission string '{perm_string}'"

    def test_create_scope_from_admin_route_object(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            fail_msg = f"Failed with admin group object no. {index}"
            assert create_scope_from_admin_route_object(admin_route_object) == scope, fail_msg

    def test_create_string_from_scope(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            assert create_string_from_scope(scope) == perm_string, f"Failed with permission string '{perm_string}'"

    def test_create_admin_route_object_from_scope(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            returned = create_admin_route_object_from_scope(scope)
            assert unordered(returned) == admin_route_object, f"Failed with admin group object no. {index}"


if __name__ == "__main__":
    pytest.main([__file__])
