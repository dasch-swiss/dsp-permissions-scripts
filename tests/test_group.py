from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import NAMES_OF_BUILTIN_GROUPS
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.group import is_valid_group_iri
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE


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
            {"id": new_custom_group_iri, "name": "btt-editors", "project": {"shortname": "btt"}},
            {"id": old_custom_group_iri, "name": "Thing searcher", "project": {"shortname": "anything"}},
        ]
    }
    dsp_client = Mock(spec=DspClient, get=Mock(return_value=get_response))
    return dsp_client


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


@pytest.mark.parametrize("prefixed_iri", ["my-shortname:my-custom-group", "ANYTHING:Thing Searcher"])
def test_custom_group(prefixed_iri: str) -> None:
    custom_group = CustomGroup(prefixed_iri=prefixed_iri)
    assert custom_group.prefixed_iri == prefixed_iri


@pytest.mark.parametrize(
    "group_name",
    [
        "knora-api:Value",
        "knora-base:Resource",
        "knora-admin:ThingSearcher",
        f"{KNORA_ADMIN_ONTO_NAMESPACE}ThingSearcher",
    ],
)
def test_custom_group_invalid(group_name: str) -> None:
    with pytest.raises(InvalidGroupError):
        CustomGroup(prefixed_iri=group_name)


def test_group_builder() -> None:
    assert group_builder("knora-admin:UnknownUser") == UNKNOWN_USER
    assert group_builder("limc_short-name:groupname") == CustomGroup(prefixed_iri="limc_short-name:groupname")


@pytest.mark.parametrize(
    "inv", ["knora-api:foo", "knora-base:foo", "knora-admin:foo", f"{KNORA_ADMIN_ONTO_NAMESPACE}foo"]
)
def test_group_builder_invalid(inv: str) -> None:
    with pytest.raises(InvalidGroupError):
        group_builder(inv)


@pytest.mark.parametrize("iri", ["knora-admin:ProjectAdmin", "project_short-name:Group Name", "limc:group-name_1", "http://rdfh.ch/groups/0001/thing-searcher"])
def test_is_valid_prefixed_group_iri_true(iri: str) -> None:
    assert is_valid_group_iri(iri)


@pytest.mark.parametrize(
    "iri",
    [
        f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin",
        "ProjectAdmin",
        "knora-base:Value",
        "knora-admin:NotExisting",
    ],
)
def test_is_valid_prefixed_group_iri_false(iri: str) -> None:
    assert not is_valid_group_iri(iri)
