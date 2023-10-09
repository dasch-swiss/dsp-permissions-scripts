import unittest

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope


class TestScope(unittest.TestCase):

    def test_scope_validation_on_creation(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            PermissionScope(
                CR={BuiltinGroup.PROJECT_ADMIN},
                D={BuiltinGroup.PROJECT_ADMIN},
                V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
            )

    def test_scope_validation_on_assignment(self) -> None:
        scope = PermissionScope(
            CR={BuiltinGroup.PROJECT_ADMIN},
            V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            scope.add("RV", BuiltinGroup.PROJECT_ADMIN)

    def test_scope_validation_on_update(self) -> None:
        scope = PermissionScope(
            CR={BuiltinGroup.PROJECT_ADMIN},
            V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
        )
        with self.assertRaisesRegex(ValueError, "must not occur in more than one field"):
            scope.add("D", BuiltinGroup.PROJECT_ADMIN)

    def test_add_to_scope(self) -> None:
        scope = PermissionScope(
            D={BuiltinGroup.SYSTEM_ADMIN},
            M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
        )
        scope.add("CR", BuiltinGroup.PROJECT_ADMIN)
        self.assertEqual(
            scope,
            PermissionScope(
                CR={BuiltinGroup.PROJECT_ADMIN},
                D={BuiltinGroup.SYSTEM_ADMIN},
                M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
            ),
        )

if __name__ == "__main__":
    unittest.main()
