import unittest

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope


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
        self.assertEqual(
            scope_added.model_dump_json(),
            PermissionScope.create(
                CR={BuiltinGroup.PROJECT_ADMIN},
                D={BuiltinGroup.SYSTEM_ADMIN},
                M={BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.KNOWN_USER},
            ).model_dump_json(),
        )

if __name__ == "__main__":
    unittest.main()
