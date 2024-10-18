from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.group import sort_groups


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


def test_sort_groups() -> None:
    groups_original = [
        group_builder("shortname:C_CustomGroup"),
        UNKNOWN_USER,
        PROJECT_ADMIN,
        PROJECT_MEMBER,
        CREATOR,
        group_builder("shortname:A_CustomGroup"),
        group_builder("shortname:B_CustomGroup"),
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
        group_builder("shortname:A_CustomGroup"),
        group_builder("shortname:B_CustomGroup"),
        group_builder("shortname:C_CustomGroup"),
    ]
    groups_returned = sort_groups(groups_original)
    assert groups_returned == groups_expected
