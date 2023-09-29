import unittest

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
    create_scope_from_admin_route_object,
    create_scope_from_string,
    create_string_from_scope,
)


class TestScopeSerialization(unittest.TestCase):
    perm_strings = [
        "CR knora-admin:SystemUser|V knora-admin:CustomGroup",
        "D knora-admin:ProjectAdmin|RV knora-admin:ProjectMember",
        "M knora-admin:ProjectAdmin|V knora-admin:Creator,knora-admin:KnownUser|RV knora-admin:UnknownUser",
        "CR knora-admin:SystemAdmin,knora-admin:ProjectAdmin|D knora-admin:Creator|RV knora-admin:UnknownUser",
    ]
    admin_route_objects = [
        [
            {"name": "CR", "additionalInformation": "knora-admin:SystemUser", "permissionCode": None},
            {"name": "V", "additionalInformation": "knora-admin:CustomGroup", "permissionCode": None},
        ],
        [
            {"name": "D", "additionalInformation": "knora-admin:ProjectAdmin", "permissionCode": None},
            {"name": "RV", "additionalInformation": "knora-admin:ProjectMember", "permissionCode": None},
        ],
        [
            {"name": "M", "additionalInformation": "knora-admin:ProjectAdmin", "permissionCode": None},
            {"name": "V", "additionalInformation": "knora-admin:Creator", "permissionCode": None},
            {"name": "V", "additionalInformation": "knora-admin:KnownUser", "permissionCode": None},
            {"name": "RV", "additionalInformation": "knora-admin:UnknownUser", "permissionCode": None},
        ],
        [
            {"name": "CR", "additionalInformation": "knora-admin:SystemAdmin", "permissionCode": None},
            {"name": "CR", "additionalInformation": "knora-admin:ProjectAdmin", "permissionCode": None},
            {"name": "D", "additionalInformation": "knora-admin:Creator", "permissionCode": None},
            {"name": "RV", "additionalInformation": "knora-admin:UnknownUser", "permissionCode": None},
        ],
    ]
    scopes = [
        PermissionScope(
            CR=[BuiltinGroup.SYSTEM_USER], 
            V=["http://www.knora.org/ontology/knora-admin#CustomGroup"]
        ),
        PermissionScope(
            D=[BuiltinGroup.PROJECT_ADMIN], 
            RV=[BuiltinGroup.PROJECT_MEMBER]
        ),
        PermissionScope(
            M=[BuiltinGroup.PROJECT_ADMIN], 
            V=[BuiltinGroup.CREATOR, BuiltinGroup.KNOWN_USER], 
            RV=[BuiltinGroup.UNKNOWN_USER]
        ),
        PermissionScope(
            CR=[BuiltinGroup.SYSTEM_ADMIN, BuiltinGroup.PROJECT_ADMIN], 
            D=[BuiltinGroup.CREATOR], 
            RV=[BuiltinGroup.UNKNOWN_USER]
        ),
    ]

    def test_create_scope_from_string(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            self.assertEqual(
                create_scope_from_string(perm_string).model_dump_json(),
                scope.model_dump_json(),
                msg=f"Failed with permission string '{perm_string}'",
            )
    
    def test_create_scope_from_admin_route_object(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            self.assertEqual(
                create_scope_from_admin_route_object(admin_route_object).model_dump_json(),
                scope.model_dump_json(),
                msg=f"Failed with admin group object no. {index}",
            )

    def test_create_string_from_scope(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            self.assertEqual(
                create_string_from_scope(scope),
                perm_string,
                msg=f"Failed with permission string '{perm_string}'",
            )

    def test_create_admin_route_object_from_scope(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            self.assertEqual(
                create_admin_route_object_from_scope(scope),
                admin_route_object,
                msg=f"Failed with admin group object no. {index}",
            )


if __name__ == "__main__":
    unittest.main()
