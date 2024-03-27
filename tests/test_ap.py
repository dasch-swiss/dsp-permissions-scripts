import unittest

from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.models import group


class TestAp(unittest.TestCase):
    ap = Ap(
        forGroup=group.UNKNOWN_USER,
        forProject="http://rdfh.ch/projects/0001",
        hasPermissions=frozenset({ApValue.ProjectResourceCreateAllPermission, ApValue.ProjectAdminGroupAllPermission}),
        iri="http://rdfh.ch/foo",
    )

    def test_add_permission(self):
        self.ap.add_permission(ApValue.ProjectAdminRightsAllPermission)
        self.assertIn(ApValue.ProjectAdminRightsAllPermission, self.ap.hasPermissions)

    def test_add_permission_already_exists(self):
        with self.assertRaises(ValueError):
            self.ap.add_permission(ApValue.ProjectAdminGroupAllPermission)

    def test_remove_permission(self):
        self.ap.remove_permission(ApValue.ProjectAdminGroupAllPermission)
        self.assertNotIn(ApValue.ProjectAdminGroupAllPermission, self.ap.hasPermissions)

    def test_remove_permission_not_exists(self):
        with self.assertRaises(ValueError):
            self.ap.remove_permission(ApValue.ProjectAdminAllPermission)
