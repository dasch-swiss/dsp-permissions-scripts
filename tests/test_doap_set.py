from typing import Any
from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.doap import doap_set
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope


@pytest.fixture
def request_for_group() -> dict[str, Any]:
    return {
        "forGroup": "http://www.knora.org/ontology/knora-admin#KnownUser",
        "forProject": "http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw",
        "forProperty": None,
        "forResourceClass": None,
        "hasPermissions": [
            {
                "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                "name": "V",
                "permissionCode": None,
            }
        ],
    }


@pytest.fixture
def response_for_group() -> dict[str, Any]:
    return {
        "default_object_access_permission": {
            "iri": "http://rdfh.ch/permissions/4123/grKNPv-tQ7aBYq0mDXyatg",
            "forProject": "http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw",
            "forGroup": "http://www.knora.org/ontology/knora-admin#KnownUser",
            "hasPermissions": [
                {
                    "name": "V",
                    "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                    "permissionCode": 2,
                }
            ],
        }
    }


def test_create_doap_for_group(request_for_group: dict[str, Any], response_for_group: dict[str, Any]) -> None:
    doap_set.get_project_iri_and_onto_iris_by_shortcode = Mock(  # type: ignore[attr-defined]
        return_value=("http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw", None)
    )
    doap_set.create_doap_from_admin_route_response = Mock()  # type: ignore[attr-defined]
    dsp_client = Mock()
    dsp_client.post = Mock(return_value=response_for_group)
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.KNOWN_USER),
        shortcode="0000",
        scope=PermissionScope.create(V=[group.UNKNOWN_USER]),
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/doap", data=request_for_group)
    doap_set.create_doap_from_admin_route_response.assert_called_once_with(  # type: ignore[attr-defined]
        response_for_group["default_object_access_permission"]
    )
