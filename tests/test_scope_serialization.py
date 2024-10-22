from unittest.mock import Mock

import pytest
from pytest_unordered import unordered

from dsp_permissions_scripts.models.group import CREATOR
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import SYSTEM_ADMIN
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.scope_serialization import create_admin_route_object_from_scope
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_admin_route_object
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope

SHORTNAME = "shortname"
SHORTCODE = "1234"
CUSTOM_GROUP_NAME = "CustomGroup"
CUSTOM_GROUP_FULL_IRI = f"http://rdfh.ch/groups/{SHORTCODE}/abcdef"


@pytest.fixture
def dsp_client() -> DspClient:
    get_response = {
        "groups": [{"id": CUSTOM_GROUP_FULL_IRI, "name": CUSTOM_GROUP_NAME, "project": {"shortname": SHORTNAME}}]
    }
    dsp_client = Mock(spec=DspClient, get=Mock(return_value=get_response))
    return dsp_client


class TestScopeSerialization:
    perm_strings = (
        f"CR knora-admin:SystemAdmin|V {SHORTNAME}:{CUSTOM_GROUP_NAME}",
        "D knora-admin:ProjectAdmin|RV knora-admin:ProjectMember",
        "M knora-admin:ProjectAdmin|V knora-admin:Creator,knora-admin:KnownUser|RV knora-admin:UnknownUser",
        "CR knora-admin:SystemAdmin,knora-admin:ProjectAdmin|D knora-admin:Creator|RV knora-admin:UnknownUser",
    )
    admin_route_objects = (
        [
            {"name": "CR", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}SystemAdmin", "permissionCode": None},
            {"name": "V", "additionalInformation": CUSTOM_GROUP_FULL_IRI, "permissionCode": None},
        ],
        [
            {"name": "D", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin", "permissionCode": None},
            {
                "name": "RV",
                "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectMember",
                "permissionCode": None,
            },
        ],
        [
            {"name": "M", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin", "permissionCode": None},
            {"name": "V", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}Creator", "permissionCode": None},
            {"name": "V", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}KnownUser", "permissionCode": None},
            {"name": "RV", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}UnknownUser", "permissionCode": None},
        ],
        [
            {"name": "CR", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}SystemAdmin", "permissionCode": None},
            {
                "name": "CR",
                "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}ProjectAdmin",
                "permissionCode": None,
            },
            {"name": "D", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}Creator", "permissionCode": None},
            {"name": "RV", "additionalInformation": f"{KNORA_ADMIN_ONTO_NAMESPACE}UnknownUser", "permissionCode": None},
        ],
    )
    scopes = (
        PermissionScope.create(
            CR=[SYSTEM_ADMIN],
            V=[CustomGroup(prefixed_iri=f"{SHORTNAME}:{CUSTOM_GROUP_NAME}")],
        ),
        PermissionScope.create(
            D=[PROJECT_ADMIN],
            RV=[PROJECT_MEMBER],
        ),
        PermissionScope.create(
            M=[PROJECT_ADMIN],
            V=[CREATOR, KNOWN_USER],
            RV=[UNKNOWN_USER],
        ),
        PermissionScope.create(
            CR=[SYSTEM_ADMIN, PROJECT_ADMIN],
            D=[CREATOR],
            RV=[UNKNOWN_USER],
        ),
    )

    def test_create_scope_from_string(self, dsp_client: DspClient) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            assert (
                create_scope_from_string(perm_string, dsp_client) == scope
            ), f"Failed with permission string '{perm_string}'"

    def test_create_scope_from_admin_route_object(self, dsp_client: DspClient) -> None:
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            fail_msg = f"Failed with admin group object no. {index}"
            returned = create_scope_from_admin_route_object(admin_route_object, dsp_client)
            assert returned == scope, fail_msg

    def test_create_string_from_scope(self) -> None:
        for perm_string, scope in zip(self.perm_strings, self.scopes):
            assert create_string_from_scope(scope) == perm_string, f"Failed with permission string '{perm_string}'"

    def test_create_admin_route_object_from_scope(self) -> None:
        get_response = {
            "groups": [{"id": CUSTOM_GROUP_FULL_IRI, "name": CUSTOM_GROUP_NAME, "project": {"shortname": SHORTNAME}}]
        }
        dsp_client_mock = Mock(spec=DspClient, get=Mock(return_value=get_response))
        for admin_route_object, scope, index in zip(self.admin_route_objects, self.scopes, range(len(self.scopes))):
            returned = create_admin_route_object_from_scope(scope, dsp_client_mock)
            assert unordered(returned) == admin_route_object, f"Failed with admin group object no. {index}"


if __name__ == "__main__":
    pytest.main([__file__])
