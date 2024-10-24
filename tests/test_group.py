import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.errors import InvalidGroupError


def test_builtin_groups() -> None:
    assert group.UNKNOWN_USER == group.Group(prefixed_iri="knora-admin:UnknownUser")
    assert group.KNOWN_USER == group.Group(prefixed_iri="knora-admin:KnownUser")
    assert group.PROJECT_MEMBER == group.Group(prefixed_iri="knora-admin:ProjectMember")
    assert group.PROJECT_ADMIN == group.Group(prefixed_iri="knora-admin:ProjectAdmin")
    assert group.CREATOR == group.Group(prefixed_iri="knora-admin:Creator")
    assert group.SYSTEM_ADMIN == group.Group(prefixed_iri="knora-admin:SystemAdmin")


def test_custom_group() -> None:
    group_iri = "knora-admin:my-custom-group"
    custom_group = group.Group(prefixed_iri=group_iri)
    assert custom_group.prefixed_iri == group_iri


def test_invalid_group() -> None:
    with pytest.raises(InvalidGroupError):
        group.Group(prefixed_iri="http://www.knora.org/v2/resources/foo")
