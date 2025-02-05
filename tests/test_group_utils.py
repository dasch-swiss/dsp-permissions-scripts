from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_permissions_scripts.models.errors import InvalidGroupError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import NAMES_OF_BUILTIN_GROUPS
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.group_utils import _get_full_iri_from_builtin_group
from dsp_permissions_scripts.models.group_utils import _get_full_iri_from_custom_group
from dsp_permissions_scripts.models.group_utils import get_full_iri_from_prefixed_iri
from dsp_permissions_scripts.models.group_utils import get_prefixed_iri_from_full_iri
from dsp_permissions_scripts.models.group_utils import sort_groups
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


def test_sort_groups() -> None:
    groups_original: list[BuiltinGroup | CustomGroup] = [
        CustomGroup(prefixed_iri="shortname:C_CustomGroup"),
        UNKNOWN_USER,
        PROJECT_ADMIN,
        PROJECT_MEMBER,
        CREATOR,
        CustomGroup(prefixed_iri="shortname:A_CustomGroup"),
        CustomGroup(prefixed_iri="shortname:B_CustomGroup"),
        KNOWN_USER,
        SYSTEM_ADMIN,
    ]
    groups_expected: list[BuiltinGroup | CustomGroup] = [
        SYSTEM_ADMIN,
        CREATOR,
        PROJECT_ADMIN,
        PROJECT_MEMBER,
        KNOWN_USER,
        UNKNOWN_USER,
        CustomGroup(prefixed_iri="shortname:A_CustomGroup"),
        CustomGroup(prefixed_iri="shortname:B_CustomGroup"),
        CustomGroup(prefixed_iri="shortname:C_CustomGroup"),
    ]
    groups_returned = sort_groups(groups_original)
    assert groups_returned == groups_expected


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


@pytest.mark.parametrize("iri", ["knora-base:Value", f"{KNORA_ADMIN_ONTO_NAMESPACE}groupname"])
def test_get_full_iri_from_prefixed_iri_invalid(iri: str) -> None:
    with pytest.raises(InvalidIRIError):
        get_full_iri_from_prefixed_iri(iri, DspClient("foo"))


@patch("dsp_permissions_scripts.models.group_utils._get_full_iri_from_builtin_group")
def test_get_full_iri_from_prefixed_iri_with_builtin_group(patched_func: Mock) -> None:
    get_full_iri_from_prefixed_iri("knora-admin:ProjectAdmin", DspClient("foo"))
    patched_func.assert_called_once_with("knora-admin", "ProjectAdmin")


@patch("dsp_permissions_scripts.models.group_utils._get_full_iri_from_custom_group")
def test_get_full_iri_from_prefixed_iri_with_custom_group(patched_func: Mock) -> None:
    dsp_client = DspClient("foo")
    get_full_iri_from_prefixed_iri("limc:groupname", dsp_client)
    patched_func.assert_called_once_with("limc", "groupname", dsp_client)


@pytest.mark.parametrize("group_name", NAMES_OF_BUILTIN_GROUPS)
def test_get_full_iri_from_builtin_group(group_name: str) -> None:
    res = _get_full_iri_from_builtin_group("knora-admin", group_name)
    assert res == f"{KNORA_ADMIN_ONTO_NAMESPACE}{group_name}"


def test_get_full_iri_from_builtin_group_invalid() -> None:
    with pytest.raises(InvalidGroupError):
        _get_full_iri_from_builtin_group("knora-admin", "NonExistent")


def test_get_full_iri_from_custom_group(dsp_client_with_2_groups: DspClient, new_custom_group_iri: str) -> None:
    res = _get_full_iri_from_custom_group("btt", "btt-editors", dsp_client_with_2_groups)
    assert res == new_custom_group_iri


def test_get_full_iri_from_custom_group_invalid(dsp_client_with_2_groups: DspClient) -> None:
    with pytest.raises(InvalidGroupError):
        _get_full_iri_from_custom_group("limc", "limc-editors", dsp_client_with_2_groups)


if __name__ == "__main__":
    pytest.main([__file__])
