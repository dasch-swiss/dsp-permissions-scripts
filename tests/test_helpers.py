import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.utils.helpers import sort_groups


def test_sort_groups() -> None:
    groups_original = [
        group.BuiltinGroup(val="knora-admin:C_CustomGroup"),
        group.UNKNOWN_USER,
        group.PROJECT_ADMIN,
        group.PROJECT_MEMBER,
        group.CREATOR,
        group.BuiltinGroup(val="knora-admin:A_CustomGroup"),
        group.BuiltinGroup(val="knora-admin:B_CustomGroup"),
        group.KNOWN_USER,
        group.SYSTEM_ADMIN,
    ]
    groups_expected = [
        group.SYSTEM_ADMIN,
        group.CREATOR,
        group.PROJECT_ADMIN,
        group.PROJECT_MEMBER,
        group.KNOWN_USER,
        group.UNKNOWN_USER,
        group.BuiltinGroup(val="knora-admin:A_CustomGroup"),
        group.BuiltinGroup(val="knora-admin:B_CustomGroup"),
        group.BuiltinGroup(val="knora-admin:C_CustomGroup"),
    ]
    groups_returned = sort_groups(groups_original)
    assert groups_returned == groups_expected


if __name__ == "__main__":
    pytest.main([__file__])
