from typing import Any
from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.ap import ap_set
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.models import group


@pytest.fixture
def create_new_ap_request() -> dict[str, Any]:
    return {
        "forGroup": "http://www.knora.org/ontology/knora-admin#Creator",
        # surprisingly, it also works with "knora-admin:Creator", without context.
        "forProject": "http://rdfh.ch/projects/QykAkmHJTPS7ervbGynSHw",
        "hasPermissions": [
            {"additionalInformation": None, "name": "ProjectResourceCreateAllPermission", "permissionCode": None}
        ],
    }


@pytest.fixture
def create_new_ap_response() -> dict[str, Any]:
    return {
        "administrative_permission": {
            "iri": "http://rdfh.ch/permissions/4123/8WIp72-IQeKjwL5y7cpNPQ",
            "forProject": "http://rdfh.ch/projects/QykAkmHJTPS7ervbGynSHw",
            "forGroup": "http://www.knora.org/ontology/knora-admin#Creator",
            "hasPermissions": [{"name": "ProjectResourceCreateAllPermission"}],
        }
    }


def test_create_new_ap_on_server(create_new_ap_request: dict[str, Any], create_new_ap_response: dict[str, Any]) -> None:
    ap_set.get_proj_iri_and_onto_iris_by_shortcode = Mock(  # type: ignore[attr-defined]
        return_value=("http://rdfh.ch/projects/QykAkmHJTPS7ervbGynSHw", None)
    )
    ap_set.create_ap_from_admin_route_object = Mock()  # type: ignore[attr-defined]
    dsp_client = Mock()
    dsp_client.post = Mock(return_value=create_new_ap_response)
    _ = create_new_ap_on_server(
        forGroup=group.CREATOR,
        shortcode="0000",
        hasPermissions=[ApValue("ProjectResourceCreateAllPermission")],
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/ap", data=create_new_ap_request)
    ap_set.create_ap_from_admin_route_object.assert_called_once_with(  # type: ignore[attr-defined]
        create_new_ap_response["administrative_permission"], dsp_client
    )
