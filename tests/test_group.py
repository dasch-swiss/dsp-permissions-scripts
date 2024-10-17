import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.errors import InvalidGroupError


def test_builtin_groups() -> None:
    assert group.UNKNOWN_USER == group.BuiltinGroup(val="knora-admin:UnknownUser")
    assert group.KNOWN_USER == group.BuiltinGroup(val="knora-admin:KnownUser")
    assert group.PROJECT_MEMBER == group.BuiltinGroup(val="knora-admin:ProjectMember")
    assert group.PROJECT_ADMIN == group.BuiltinGroup(val="knora-admin:ProjectAdmin")
    assert group.CREATOR == group.BuiltinGroup(val="knora-admin:Creator")
    assert group.SYSTEM_ADMIN == group.BuiltinGroup(val="knora-admin:SystemAdmin")


def test_custom_group() -> None:
    group_iri = "knora-admin:my-custom-group"
    custom_group = group.BuiltinGroup(val=group_iri)
    assert custom_group.val == group_iri


def test_invalid_group() -> None:
    with pytest.raises(InvalidGroupError):
        group.BuiltinGroup(val="http://www.knora.org/v2/resources/foo")
