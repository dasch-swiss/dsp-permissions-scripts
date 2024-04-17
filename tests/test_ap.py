import pytest

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.models import group


class TestAp:
    ap = Ap(
        forGroup=group.UNKNOWN_USER,
        forProject="http://rdfh.ch/projects/0001",
        hasPermissions=frozenset({ApValue.ProjectResourceCreateAllPermission, ApValue.ProjectAdminGroupAllPermission}),
        iri="http://rdfh.ch/foo",
    )

    def test_add_permission(self) -> None:
        self.ap.add_permission(ApValue.ProjectAdminRightsAllPermission)
        assert ApValue.ProjectAdminRightsAllPermission in self.ap.hasPermissions

    def test_add_permission_already_exists(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011 (exception too broad)
            self.ap.add_permission(ApValue.ProjectAdminGroupAllPermission)

    def test_remove_permission(self) -> None:
        self.ap.remove_permission(ApValue.ProjectAdminGroupAllPermission)
        assert ApValue.ProjectAdminGroupAllPermission not in self.ap.hasPermissions

    def test_remove_permission_not_exists(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011 (exception too broad)
            self.ap.remove_permission(ApValue.ProjectAdminAllPermission)
