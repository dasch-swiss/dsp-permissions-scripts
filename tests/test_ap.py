import unittest

from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.models import builtin_groups


class TestAp(unittest.TestCase):
    ap = Ap(
        forGroup=builtin_groups.UNKNOWN_USER,
        forProject="http://rdfh.ch/projects/0001",
        hasPermissions=frozenset({ApValue.ProjectResourceCreateAllPermission, ApValue.ProjectAdminGroupAllPermission}),
        iri="http://rdfh.ch/foo",
    )

    def test_add_permission(self) -> None:
        self.ap.add_permission(ApValue.ProjectAdminRightsAllPermission)
        self.assertIn(ApValue.ProjectAdminRightsAllPermission, self.ap.hasPermissions)

    def test_add_permission_already_exists(self) -> None:
        with self.assertRaises(ValueError):
            self.ap.add_permission(ApValue.ProjectAdminGroupAllPermission)

    def test_remove_permission(self) -> None:
        self.ap.remove_permission(ApValue.ProjectAdminGroupAllPermission)
        self.assertNotIn(ApValue.ProjectAdminGroupAllPermission, self.ap.hasPermissions)

    def test_remove_permission_not_exists(self) -> None:
        with self.assertRaises(ValueError):
            self.ap.remove_permission(ApValue.ProjectAdminAllPermission)
