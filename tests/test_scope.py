import unittest

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope
from tests.test_scope_serialization import compare_scopes


class TestScope(unittest.TestCase):

    def test_scope_validation_on_creation(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            PermissionScope.create(
                CR={BuiltinGroup.PROJECT_ADMIN},
                D={BuiltinGroup.PROJECT_ADMIN},
                V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
            )

    def test_scope_validation_on_add_to_same_permission(self) -> None:
        scope = PermissionScope.create(
            CR={BuiltinGroup.PROJECT_ADMIN},
            V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
        )
        with self.assertRaisesRegex(
            ValueError, 
            "Group 'http://www.knora.org/ontology/knora-admin#ProjectAdmin' is already in permission 'CR'"
        ):
            _ = scope.add("CR", BuiltinGroup.PROJECT_ADMIN)

    def test_scope_validation_on_add_to_different_permission(self) -> None:
        scope = PermissionScope.create(
            CR={BuiltinGroup.PROJECT_ADMIN},
            V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            _ = scope.add("RV", BuiltinGroup.PROJECT_ADMIN)

    def test_add_to_scope(self) -> None:
        scope = PermissionScope.create(
            D={BuiltinGroup.SYSTEM_ADMIN},
            M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
        )
        scope_added = scope.add("CR", BuiltinGroup.PROJECT_ADMIN)
        compare_scopes(
            scope1=scope_added,
            scope2=PermissionScope.create(
                CR={BuiltinGroup.PROJECT_ADMIN},
                D={BuiltinGroup.SYSTEM_ADMIN},
                M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
            ),
        )

    def test_remove_inexisting_group(self) -> None:
        scope = PermissionScope.create(
            D={BuiltinGroup.SYSTEM_ADMIN},
            M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "is not in permission 'D'"):
            _ = scope.remove("D", BuiltinGroup.UNKNOWN_USER)
        
    def test_remove_from_empty_perm(self) -> None:
        scope = PermissionScope.create(
            D={BuiltinGroup.PROJECT_ADMIN},
            V={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.UNKNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "is not in permission 'CR'"):
            _ = scope.remove("CR", BuiltinGroup.PROJECT_ADMIN)

    def test_remove_from_scope(self) -> None:
        scope = PermissionScope.create(
            CR={BuiltinGroup.PROJECT_ADMIN},
            D={BuiltinGroup.SYSTEM_ADMIN},
            M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
        )
        scope_removed = scope.remove("CR", BuiltinGroup.PROJECT_ADMIN)
        compare_scopes(
            scope1=scope_removed,
            scope2=PermissionScope.create(
                D={BuiltinGroup.SYSTEM_ADMIN},
                M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
            ),
        )

if __name__ == "__main__":
    unittest.main()
