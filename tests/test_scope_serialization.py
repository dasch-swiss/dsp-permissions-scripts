import unittest
from typing import Any

from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
    create_scope_from_admin_route_object,
    create_scope_from_string,
    create_string_from_scope,
)


class TestScopeSerialization(unittest.TestCase):
    perm_strings_to_admin_route_object: dict[str, list[dict[str, Any]]] = {}

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        perm_strings = [
            "CR knora-admin:SystemUser|V knora-admin:CustomGroup",
            "D knora-admin:ProjectAdmin|RV knora-admin:ProjectMember",
            "M knora-admin:ProjectAdmin|V knora-admin:Creator,knora-admin:KnownUser|RV knora-admin:UnknownUser",
            (
                "CR knora-admin:SystemAdmin,knora-admin:ProjectAdmin|D knora-admin:Creator|"
                "RV knora-admin:KnownUser,knora-admin:UnknownUser"
            ),
        ]
        cls.perm_strings_to_admin_route_object[perm_strings[0]] = [
            {"name": "CR", "additionalInformation": "knora-admin:SystemUser"},
            {"name": "V", "additionalInformation": "knora-admin:CustomGroup"},
        ]
        cls.perm_strings_to_admin_route_object[perm_strings[1]] = [
            {"name": "D", "additionalInformation": "knora-admin:ProjectAdmin"},
            {"name": "RV", "additionalInformation": "knora-admin:ProjectMember"},
        ]
        cls.perm_strings_to_admin_route_object[perm_strings[2]] = [
            {"name": "M", "additionalInformation": "knora-admin:ProjectAdmin"},
            {"name": "V", "additionalInformation": "knora-admin:Creator"}, 
            {"name": "V", "additionalInformation":"knora-admin:KnownUser"},
            {"name": "RV", "additionalInformation": "knora-admin:UnknownUser"},
        ]
        cls.perm_strings_to_admin_route_object[perm_strings[3]] = [
            {"name": "CR", "additionalInformation": "knora-admin:SystemAdmin"}, 
            {"name": "CR", "additionalInformation": "knora-admin:ProjectAdmin"},
            {"name": "D", "additionalInformation": "knora-admin:Creator"},
            {"name": "RV", "additionalInformation": "knora-admin:KnownUser"}, 
            {"name": "RV", "additionalInformation": "knora-admin:UnknownUser"},
        ]
        for _, admin_route_object in cls.perm_strings_to_admin_route_object.items():
            for elem in admin_route_object:
                elem["permissionCode"] = None

    def test_perm_string_of_scope_equals_to_orig_string(self) -> None:
        for perm_string in self.perm_strings_to_admin_route_object:
            scope = create_scope_from_string(perm_string)
            perm_string_new = create_string_from_scope(scope)
            self.assertEqual(perm_string, perm_string_new)

    def test_as_admin_route_object_equals_to_orig_object(self) -> None:
        for perm_string, admin_route_object in self.perm_strings_to_admin_route_object.items():
            scope = create_scope_from_admin_route_object(admin_route_object)
            admin_route_object_new = create_admin_route_object_from_scope(scope)
            self.assertEqual(
                admin_route_object, 
                admin_route_object_new,
                msg=f"Failed with admin group object of permission string '{perm_string}'"
            )

    def test_as_admin_route_object_equals_to_expected_object(self) -> None:
        for perm_string, admin_route_object in self.perm_strings_to_admin_route_object.items():
            scope = create_scope_from_string(perm_string)
            admin_route_object_new = create_admin_route_object_from_scope(scope)
            self.assertEqual(
                admin_route_object, 
                admin_route_object_new,
                msg=f"Failed with permission string '{perm_string}'"
            )

if __name__ == '__main__':
    unittest.main()
