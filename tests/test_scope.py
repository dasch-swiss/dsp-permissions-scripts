import unittest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from tests.test_scope_serialization import compare_scopes


class TestScope(unittest.TestCase):
    def test_scope_validation_on_creation(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            PermissionScope.create(
                CR={group.PROJECT_ADMIN},
                D={group.PROJECT_ADMIN},
                V={group.UNKNOWN_USER, group.KNOWN_USER},
            )

    def test_scope_validation_on_add_to_same_permission(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            V={group.UNKNOWN_USER, group.KNOWN_USER},
        )
        with self.assertRaisesRegex(
            ValueError, "Group 'val='http://www.knora.org/ontology/knora-admin#ProjectAdmin'' is already in permission 'CR'"
        ):
            _ = scope.add("CR", group.PROJECT_ADMIN)

    def test_scope_validation_on_add_to_different_permission(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            V={group.UNKNOWN_USER, group.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            _ = scope.add("RV", group.PROJECT_ADMIN)

    def test_add_to_scope(self) -> None:
        scope = PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        scope_added = scope.add("CR", group.PROJECT_ADMIN)
        compare_scopes(
            scope1=scope_added,
            scope2=PermissionScope.create(
                CR={group.PROJECT_ADMIN},
                D={group.SYSTEM_ADMIN},
                M={group.PROJECT_MEMBER, group.KNOWN_USER},
            ),
        )

    def test_remove_inexisting_group(self) -> None:
        scope = PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "is not in permission 'D'"):
            _ = scope.remove("D", group.UNKNOWN_USER)

    def test_remove_from_empty_perm(self) -> None:
        scope = PermissionScope.create(
            D={group.PROJECT_ADMIN},
            V={group.PROJECT_MEMBER, group.UNKNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "is not in permission 'CR'"):
            _ = scope.remove("CR", group.PROJECT_ADMIN)

    def test_remove_from_scope(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        scope_removed = scope.remove("CR", group.PROJECT_ADMIN)
        compare_scopes(
            scope1=scope_removed,
            scope2=PermissionScope.create(
                D={group.SYSTEM_ADMIN},
                M={group.PROJECT_MEMBER, group.KNOWN_USER},
            ),
        )


if __name__ == "__main__":
    unittest.main()
