import pytest

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import group_builder


def test_builtin_groups() -> None:
    assert UNKNOWN_USER == group_builder("knora-admin:UnknownUser")
    assert KNOWN_USER == group_builder("knora-admin:KnownUser")
    assert PROJECT_MEMBER == group_builder("knora-admin:ProjectMember")
    assert PROJECT_ADMIN == group_builder("knora-admin:ProjectAdmin")
    assert CREATOR == group_builder("knora-admin:Creator")
    assert SYSTEM_ADMIN == group_builder("knora-admin:SystemAdmin")


def test_custom_group() -> None:
    group_iri = "knora-admin:my-custom-group"
    custom_group = group_builder(group_iri)
    assert custom_group.prefixed_iri == group_iri


def test_invalid_group() -> None:
    with pytest.raises(InvalidGroupError):
        group_builder("http://www.knora.org/v2/resources/foo")
