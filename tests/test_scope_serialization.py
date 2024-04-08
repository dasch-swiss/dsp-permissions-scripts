import unittest
from typing import Any

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
)
from dsp_permissions_scripts.utils.scope_serialization import (
    create_scope_from_admin_route_object,
)
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope


def compare_scopes(
    scope1: PermissionScope,
    scope2: PermissionScope,
    msg: str | None = None,
) -> None:
    scope1_dict = scope1.model_dump(mode="json")
    scope1_dict = {k: sorted(v, key=lambda x: x["val"]) for k, v in scope1_dict.items()}
    scope2_dict = scope2.model_dump(mode="json")
    scope2_dict = {k: sorted(v, key=lambda x: x["val"]) for k, v in scope2_dict.items()}
    unittest.TestCase().assertDictEqual(scope1_dict, scope2_dict, msg=msg)


class TestScopeSerialization(unittest.TestCase):
    perm_strings = [
        "CR knora-admin:SystemAdmin|V knora-admin:CustomGroup",
        "D knora-admin:ProjectAdmin|RV knora-admin:ProjectMember",
        "M knora-admin:ProjectAdmin|V knora-admin:Creator,knora-admin:KnownUser|RV knora-admin:UnknownUser",
        "CR knora-admin:SystemAdmin,knora-admin:ProjectAdmin|D knora-admin:Creator|RV knora-admin:UnknownUser",
    ]
    admin_route_objects = [
        [
            {"name": "CR", "additionalInformation": "knora-admin:SystemAdmin", "permissionCode": None},
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
        PermissionScope.create(
            CR=[group.SYSTEM_ADMIN],
            V=[group.Group(val="http://www.knora.org/ontology/knora-admin#CustomGroup")],
        ),
        PermissionScope.create(
            D={group.PROJECT_ADMIN},
            RV={group.PROJECT_MEMBER},
        ),
        PermissionScope.create(
            M={group.PROJECT_ADMIN},
            V={group.CREATOR, group.KNOWN_USER},
            RV={group.UNKNOWN_USER},
        ),
        PermissionScope.create(
            CR={group.SYSTEM_ADMIN, group.PROJECT_ADMIN},
            D={group.CREATOR},
            RV={group.UNKNOWN_USER},
        ),
    ]

    def test_create_scope_from_string(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            compare_scopes(
                scope1=create_scope_from_string(perm_string),
                scope2=scope,
                msg=f"Failed with permission string '{perm_string}'",
            )

    def test_create_scope_from_admin_route_object(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            compare_scopes(
                scope1=create_scope_from_admin_route_object(admin_route_object),
                scope2=scope,
                msg=f"Failed with admin group object no. {index}",
            )

    def test_create_string_from_scope(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            perm_string_full = self._resolve_prefixes_of_perm_string(perm_string)
            self.assertEqual(
                create_string_from_scope(scope),
                perm_string_full,
                msg=f"Failed with permission string '{perm_string}'",
            )

    def test_create_admin_route_object_from_scope(self) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            admin_route_object_full = self._resolve_prefixes_of_admin_route_object(admin_route_object)
            self.assertCountEqual(
                create_admin_route_object_from_scope(scope),
                admin_route_object_full,
                msg=f"Failed with admin group object no. {index}",
            )

    def _resolve_prefixes_of_admin_route_object(self, admin_route_object: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for obj in admin_route_object:
            obj["additionalInformation"] = obj["additionalInformation"].replace(
                "knora-admin:", "http://www.knora.org/ontology/knora-admin#"
            )
        return admin_route_object

    def _resolve_prefixes_of_perm_string(self, perm_string: str) -> str:
        return perm_string.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#")


if __name__ == "__main__":
    unittest.main()
