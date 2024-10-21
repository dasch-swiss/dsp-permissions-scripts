from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import NAMES_OF_BUILTIN_GROUPS
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.group import get_prefixed_iri_from_full_iri
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.group import is_prefixed_group_iri
from dsp_permissions_scripts.models.group import sort_groups
from dsp_permissions_scripts.utils.dsp_client import DspClient


@pytest.fixture
def new_custom_group_iri() -> str:
    return "http://rdfh.ch/groups/083A/_zbeAt-lQDSUNItmBBafvw"


@pytest.fixture
def old_custom_group_iri() -> str:
    return "http://rdfh.ch/groups/0001/thing-searcher"


@pytest.fixture
def dsp_client_with_2_groups(new_custom_group_iri: str, old_custom_group_iri: str) -> DspClient:
    get_response = {
        "groups": [
            {"id": new_custom_group_iri, "name": "btt-editors", "project": {"shortname": "btt", "shortcode": "083A"}},
            {
                "id": old_custom_group_iri,
                "name": "Thing searcher",
                "project": {"shortname": "anything", "shortcode": "0001"},
            },
        ]
    }
    dsp_client = Mock(spec=DspClient)
    dsp_client.get = Mock(return_value=get_response)
    return dsp_client


def test_is_prefixed_iri() -> None:
    assert is_prefixed_group_iri("knora-admin:ProjectAdmin")
    assert not is_prefixed_group_iri(f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin")
    with pytest.raises(InvalidIRIError):
        is_prefixed_group_iri("ProjectAdmin")


@pytest.mark.parametrize("group_name", NAMES_OF_BUILTIN_GROUPS)
def test_get_prefixed_iri_from_full_iri_builtin(group_name: str) -> None:
    returned = get_prefixed_iri_from_full_iri(f"{KNORA_ADMIN_ONTO_NAMESPACE}{group_name}", DspClient("foo"))
    assert returned == f"knora-admin:{group_name}"


def test_get_prefixed_iri_from_full_iri_custom(dsp_client_with_2_groups: DspClient) -> None:
    new_group_iri = "http://rdfh.ch/groups/083A/_zbeAt-lQDSUNItmBBafvw"
    old_group_iri = "http://rdfh.ch/groups/0001/thing-searcher"
    new_group_iri_returned = get_prefixed_iri_from_full_iri(new_group_iri, dsp_client_with_2_groups)
    old_group_iri_returned = get_prefixed_iri_from_full_iri(old_group_iri, dsp_client_with_2_groups)
    assert new_group_iri_returned == "btt:btt-editors"
    assert old_group_iri_returned == "anything:Thing searcher"


@pytest.mark.parametrize(
    "iri",
    ["http://www.knora.org/ontology/knora-admin#Thing searcher", "http://www.knora.org/ontology/knora-base#Value"],
)
def test_get_prefixed_iri_from_full_iri_invalid_iri(iri: str) -> None:
    with pytest.raises(InvalidIRIError):
        get_prefixed_iri_from_full_iri(iri, DspClient("foo"))


def test_get_prefixed_iri_from_full_iri_invalid_group(dsp_client_with_2_groups: DspClient) -> None:
    with pytest.raises(InvalidGroupError):
        get_prefixed_iri_from_full_iri("http://rdfh.ch/groups/0123/8-5f7B639_79ef6a043baW", dsp_client_with_2_groups)


@pytest.mark.parametrize("group_name", NAMES_OF_BUILTIN_GROUPS)
def test_builtin_group_from_prefixed_iri(group_name: str) -> None:
    builtin_group = BuiltinGroup(prefixed_iri=f"knora-admin:{group_name}")
    assert builtin_group in [SYSTEM_ADMIN, CREATOR, PROJECT_ADMIN, PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER]


@pytest.mark.parametrize("group_name", NAMES_OF_BUILTIN_GROUPS)
def test_builtin_group_from_full_iri_raises(group_name: str) -> None:
    with pytest.raises(InvalidGroupError):
        BuiltinGroup(prefixed_iri=f"{KNORA_ADMIN_ONTO_NAMESPACE}{group_name}")


def test_builtin_group_invalid_prefix() -> None:
    invalid_prefixes = ["limc", "knora-api", "knora-base"]
    for prefix in invalid_prefixes:
        with pytest.raises(InvalidGroupError):
            BuiltinGroup(prefixed_iri=f"{prefix}:ProjectAdmin")


def test_builtin_group_invalid_name() -> None:
    invalid_names = ["SystemAdministrator", "Sysadmin", "ProjectAdministator", "ProjAdmin", "ProjMember"]
    for inv in invalid_names:
        with pytest.raises(InvalidGroupError):
            BuiltinGroup(prefixed_iri=f"knora-admin:{inv}")


@pytest.mark.parametrize("group_name", NAMES_OF_BUILTIN_GROUPS)
def test_builtin_group_generate_full_iri(group_name: str) -> None:
    generated_full_iri = BuiltinGroup(prefixed_iri=f"knora-admin:{group_name}").full_iri()
    assert generated_full_iri == f"{KNORA_ADMIN_ONTO_NAMESPACE}{group_name}"


@pytest.mark.parametrize("prefixed_iri", ["my-shortname:my-custom-group", "ANYTHING:Thing Searcher"])
def test_custom_group(prefixed_iri: str) -> None:
    custom_group = CustomGroup(prefixed_iri=prefixed_iri)
    assert custom_group.prefixed_iri == prefixed_iri


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
