import pytest

from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.group_utils import sort_groups


def test_sort_groups() -> None:
    groups_original = [
        Group(prefixed_iri="knora-admin:C_CustomGroup"),
        UNKNOWN_USER,
        PROJECT_ADMIN,
        PROJECT_MEMBER,
        CREATOR,
        Group(prefixed_iri="knora-admin:A_CustomGroup"),
        Group(prefixed_iri="knora-admin:B_CustomGroup"),
        KNOWN_USER,
        SYSTEM_ADMIN,
    ]
    groups_expected = [
        SYSTEM_ADMIN,
        CREATOR,
        PROJECT_ADMIN,
        PROJECT_MEMBER,
        KNOWN_USER,
        UNKNOWN_USER,
        Group(prefixed_iri="knora-admin:A_CustomGroup"),
        Group(prefixed_iri="knora-admin:B_CustomGroup"),
        Group(prefixed_iri="knora-admin:C_CustomGroup"),
    ]
    groups_returned = sort_groups(groups_original)
    assert groups_returned == groups_expected


if __name__ == "__main__":
    pytest.main([__file__])
