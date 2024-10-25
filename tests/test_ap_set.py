from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.models import group

PROJ_IRI = "http://rdfh.ch/projects/QykAkmHJTPS7ervbGynSHw"
PROJ_SHORTCODE = "0000"


@pytest.fixture
def create_new_ap_request() -> dict[str, Any]:
    return {
        "forGroup": "http://www.knora.org/ontology/knora-admin#Creator",
        # surprisingly, it also works with "knora-admin:Creator", without context.
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": None, "name": "ProjectResourceCreateAllPermission", "permissionCode": None}
        ],
    }


@pytest.fixture
def create_new_ap_response() -> dict[str, Any]:
    return {
        "administrative_permission": {
            "iri": "http://rdfh.ch/permissions/4123/8WIp72-IQeKjwL5y7cpNPQ",
            "forProject": PROJ_IRI,
            "forGroup": "http://www.knora.org/ontology/knora-admin#Creator",
            "hasPermissions": [{"name": "ProjectResourceCreateAllPermission"}],
        }
    }


@patch("dsp_permissions_scripts.ap.ap_set.get_proj_iri_and_onto_iris_by_shortcode", return_value=(PROJ_IRI, None))
@patch("dsp_permissions_scripts.ap.ap_set.create_ap_from_admin_route_object")
def test_create_new_ap_on_server(
    create_ap_from_admin_route_object: Mock,
    get_proj_iri_and_onto_iris_by_shortcode: Mock,  # noqa: ARG001
    create_new_ap_request: dict[str, Any],
    create_new_ap_response: dict[str, Any],
) -> None:
    dsp_client = Mock(post=Mock(return_value=create_new_ap_response))
    _ = create_new_ap_on_server(
        forGroup=group.CREATOR,
        shortcode=PROJ_SHORTCODE,
        hasPermissions=[ApValue("ProjectResourceCreateAllPermission")],
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/ap", data=create_new_ap_request)
    create_ap_from_admin_route_object.assert_called_once_with(create_new_ap_response["administrative_permission"], dsp_client)
