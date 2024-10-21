import pytest

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.group import sort_groups

NAMES_OF_BUILTIN_GROUPS = ["SystemAdmin", "Creator", "ProjectAdmin", "ProjectMember", "KnownUser", "UnknownUser"]


def test_builtin_group_from_prefixed_iri() -> None:
    builtin_groups = [BuiltinGroup(prefixed_iri=f"knora-admin:{x}") for x in NAMES_OF_BUILTIN_GROUPS]
    assert builtin_groups == [SYSTEM_ADMIN, CREATOR, PROJECT_ADMIN, PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER]


def test_builtin_group_from_full_iri_raises() -> None:
    full_iris = [f"{KNORA_ADMIN_ONTO_NAMESPACE}{x}" for x in NAMES_OF_BUILTIN_GROUPS]
    for full_iri in full_iris:
        with pytest.raises(InvalidGroupError):
            BuiltinGroup(prefixed_iri=full_iri)


def test_builtin_group_invalid_prefix() -> None:
    invalid_prefixes = ["limc", "knora-api", "knora-base"]
    for prefix in invalid_prefixes:
        with pytest.raises(InvalidGroupError):
            BuiltinGroup(prefixed_iri=f"{prefix}:ProjectAdmin")


def test_builtin_group_invalid_name() -> None:
    pass


def test_custom_group() -> None:
    group_iri = "my-shortname:my-custom-group"
    custom_group = group_builder(group_iri)
    assert isinstance(custom_group, CustomGroup)
    assert custom_group.prefixed_iri == group_iri


def test_group_builder() -> None:
    pass


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
