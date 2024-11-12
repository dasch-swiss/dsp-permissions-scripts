from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_permissions_scripts.doap.doap_model import NewEntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope

SHORTCODE = "0000"
ONTO_NAME = "limc"
MY_RESCLASS_NAME = "MyResclass"
MY_PROP_NAME = "hasProperty"
PROJ_IRI = "http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw"
HTTP_HOST = "http://api.dev.dasch.swiss"
HTTPS_HOST = "https://api.dev.dasch.swiss"


@pytest.fixture
def request_for_group() -> dict[str, Any]:
    return {
        "forGroup": "http://www.knora.org/ontology/knora-admin#KnownUser",
        "forProject": PROJ_IRI,
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
            "forProject": PROJ_IRI,
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


@pytest.fixture
def request_for_resclass() -> dict[str, Any]:
    return {
        "forGroup": None,
        "forProject": PROJ_IRI,
        "forProperty": None,
        "forResourceClass": f"{HTTP_HOST}/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}",
        "hasPermissions": [
            {
                "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                "name": "V",
                "permissionCode": None,
            }
        ],
    }


@pytest.fixture
def response_for_resclass() -> dict[str, Any]:
    return {
        "default_object_access_permission": {
            "iri": "http://rdfh.ch/permissions/4123/grKNPv-tQ7aBYq0mDXyatg",
            "forProject": PROJ_IRI,
            "forResourceClass": f"{HTTP_HOST}/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}",
            "hasPermissions": [
                {
                    "name": "V",
                    "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                    "permissionCode": 2,
                }
            ],
        }
    }


@pytest.fixture
def request_for_prop() -> dict[str, Any]:
    return {
        "forGroup": None,
        "forProject": PROJ_IRI,
        "forResourceClass": None,
        "forProperty": f"{HTTP_HOST}/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}",
        "hasPermissions": [
            {
                "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                "name": "V",
                "permissionCode": None,
            }
        ],
    }


@pytest.fixture
def response_for_prop() -> dict[str, Any]:
    return {
        "default_object_access_permission": {
            "iri": "http://rdfh.ch/permissions/4123/grKNPv-tQ7aBYq0mDXyatg",
            "forProject": PROJ_IRI,
            "forProperty": f"{HTTP_HOST}/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}",
            "hasPermissions": [
                {
                    "name": "V",
                    "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
                    "permissionCode": 2,
                }
            ],
        }
    }


@patch("dsp_permissions_scripts.doap.doap_set.create_doap_from_admin_route_response")
@patch("dsp_permissions_scripts.doap.doap_set.get_proj_iri_and_onto_iris_by_shortcode", return_value=(PROJ_IRI, None))
def test_create_doap_for_group(
    get_project_iri_and_onto_iris_by_shortcode: Mock,  # noqa: ARG001
    create_doap_from_admin_route_response: Mock,
    request_for_group: dict[str, Any],
    response_for_group: dict[str, Any],
) -> None:
    dsp_client = Mock(post=Mock(return_value=response_for_group))
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.KNOWN_USER),
        shortcode=SHORTCODE,
        scope=PermissionScope.create(V=[group.UNKNOWN_USER]),
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/doap", data=request_for_group)
    create_doap_from_admin_route_response.assert_called_once_with(
        response_for_group["default_object_access_permission"], dsp_client
    )


@patch("dsp_permissions_scripts.doap.doap_set.create_doap_from_admin_route_response")
@patch("dsp_permissions_scripts.doap.doap_set.get_proj_iri_and_onto_iris_by_shortcode", return_value=(PROJ_IRI, None))
def test_create_doap_for_resclass(
    get_project_iri_and_onto_iris_by_shortcode: Mock,  # noqa: ARG001
    create_doap_from_admin_route_response: Mock,
    request_for_resclass: dict[str, Any],
    response_for_resclass: dict[str, Any],
) -> None:
    dsp_client = Mock(post=Mock(return_value=response_for_resclass), server=HTTPS_HOST)
    _ = create_new_doap_on_server(
        target=NewEntityDoapTarget(prefixed_class=f"{ONTO_NAME}:{MY_RESCLASS_NAME}"),
        shortcode=SHORTCODE,
        scope=PermissionScope.create(V=[group.UNKNOWN_USER]),
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/doap", data=request_for_resclass)
    create_doap_from_admin_route_response.assert_called_once_with(
        response_for_resclass["default_object_access_permission"], dsp_client
    )


@patch("dsp_permissions_scripts.doap.doap_set.create_doap_from_admin_route_response")
@patch("dsp_permissions_scripts.doap.doap_set.get_proj_iri_and_onto_iris_by_shortcode", return_value=(PROJ_IRI, None))
def test_create_doap_for_prop(
    get_project_iri_and_onto_iris_by_shortcode: Mock,  # noqa: ARG001
    create_doap_from_admin_route_response: Mock,
    request_for_prop: dict[str, Any],
    response_for_prop: dict[str, Any],
) -> None:
    dsp_client = Mock(post=Mock(return_value=response_for_prop), server=HTTPS_HOST)
    _ = create_new_doap_on_server(
        target=NewEntityDoapTarget(prefixed_prop=f"{ONTO_NAME}:{MY_PROP_NAME}"),
        shortcode=SHORTCODE,
        scope=PermissionScope.create(V=[group.UNKNOWN_USER]),
        dsp_client=dsp_client,
    )
    dsp_client.post.assert_called_once_with("/admin/permissions/doap", data=request_for_prop)
    create_doap_from_admin_route_response.assert_called_once_with(
        response_for_prop["default_object_access_permission"], dsp_client
    )
