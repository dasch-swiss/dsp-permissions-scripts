from typing import Any
from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import _get_oap_of_one_resource
from dsp_permissions_scripts.oap.oap_get import _get_oaps_of_one_kb_resclass
from dsp_permissions_scripts.oap.oap_get import get_value_oaps
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.utils.dsp_client import DspClient


@pytest.fixture()
def resource() -> dict[str, Any]:
    return {
        "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        "@type": "my-data-model:ImageThing",
        "knora-api:hasPermissions": "CR knora-admin:ProjectMember|V knora-admin:UnknownUser",
        "my-data-model:hasFirstProp": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
            "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            "@type": "knora-api:TextValue",
        },
        "my-data-model:hasSecondProp": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
            "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ziOT-nhmQiqvCV8LSxAyHA",
            "@type": "knora-api:TextValue",
        },
    }


def test_oap_get_multiple_values_per_prop() -> None:
    resource = {
        "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        "geoarch:hasDescriptionSiteProject": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            "@type": "knora-api:TextValue",
        },
        "geoarch:hasFurtherDisciplines": [
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|M knora-admin:ProjectMember",
                "@type": "knora-api:ListValue",
                "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ZC-1hUiMR0mVXdaCBg1jsA",
            },
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|M knora-admin:ProjectMember",
                "@type": "knora-api:ListValue",
                "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/FMJ3-eUARl-shQ6ZbUn9aw",
            },
        ],
    }
    expected = [
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER, group.UNKNOWN_USER]),
            property="geoarch:hasDescriptionSiteProject",
            value_type="knora-api:TextValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], M=[group.PROJECT_MEMBER]),
            property="geoarch:hasFurtherDisciplines",
            value_type="knora-api:ListValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ZC-1hUiMR0mVXdaCBg1jsA",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], M=[group.PROJECT_MEMBER]),
            property="geoarch:hasFurtherDisciplines",
            value_type="knora-api:ListValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/FMJ3-eUARl-shQ6ZbUn9aw",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
    ]
    returned = get_value_oaps(resource)
    assert expected == returned


def test_get_oap_of_one_resource_no_classes() -> None:
    resource = {
        "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        "@type": "my-data-model:ImageThing",
        "knora-api:hasPermissions": "CR knora-admin:ProjectMember|V knora-admin:UnknownUser",
    }
    config = OapRetrieveConfig(retrieve_resources="none", retrieve_values="all")
    res = _get_oap_of_one_resource(resource, config)
    assert not res


def test_get_oap_of_one_resource_no_classes_all_values() -> None:
    resource = {
        "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        "@type": "my-data-model:ImageThing",
        "knora-api:hasPermissions": "CR knora-admin:ProjectMember|V knora-admin:UnknownUser",
        "my-data-model:hasFirstProp": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
            "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            "@type": "knora-api:TextValue",
        },
    }
    config = OapRetrieveConfig(retrieve_resources="none", retrieve_values="all")
    expected_val_oap = ValueOap(
        scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER]),
        property="my-data-model:hasFirstProp",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected = Oap(resource_oap=None, value_oaps=[expected_val_oap])
    res = _get_oap_of_one_resource(resource, config)
    assert res == expected


def test_get_oap_of_one_resource_no_classes_some_values(resource: dict[str, Any]) -> None:
    config = OapRetrieveConfig(
        retrieve_resources="none",
        retrieve_values="specified_props",
        specified_props=["my-data-model:hasFirstProp"],
    )
    expected_val_oap = ValueOap(
        scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER]),
        property="my-data-model:hasFirstProp",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected = Oap(resource_oap=None, value_oaps=[expected_val_oap])
    res = _get_oap_of_one_resource(resource, config)
    assert res == expected


def test_get_oap_of_one_resource_all_classes_all_values(resource: dict[str, Any]) -> None:
    config = OapRetrieveConfig(retrieve_resources="all", retrieve_values="all")
    expected_res_oap = ResourceOap(
        scope=PermissionScope.create(CR=[group.PROJECT_MEMBER], V=[group.UNKNOWN_USER]),
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected_val_oap_1 = ValueOap(
        scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER]),
        property="my-data-model:hasFirstProp",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected_val_oap_2 = ValueOap(
        scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER]),
        property="my-data-model:hasSecondProp",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ziOT-nhmQiqvCV8LSxAyHA",
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected = Oap(resource_oap=expected_res_oap, value_oaps=[expected_val_oap_1, expected_val_oap_2])
    res = _get_oap_of_one_resource(resource, config)
    assert res == expected


def test_get_oap_of_one_resource_all_classes_no_values(resource: dict[str, Any]) -> None:
    config = OapRetrieveConfig(retrieve_resources="all", retrieve_values="none")
    expected_res_oap = ResourceOap(
        scope=PermissionScope.create(CR=[group.PROJECT_MEMBER], V=[group.UNKNOWN_USER]),
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected = Oap(resource_oap=expected_res_oap, value_oaps=[])
    res = _get_oap_of_one_resource(resource, config)
    assert res == expected


def test_get_oap_of_one_resource_some_classes_some_values(resource: dict[str, Any]) -> None:
    config = OapRetrieveConfig(
        retrieve_resources="specified_res_classes",
        specified_res_classes=["my-data-model:ImageThing"],
        retrieve_values="specified_props",
        specified_props=["my-data-model:hasSecondProp"],
    )
    expected_res_oap = ResourceOap(
        scope=PermissionScope.create(CR=[group.PROJECT_MEMBER], V=[group.UNKNOWN_USER]),
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected_val_oap = ValueOap(
        scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER]),
        property="my-data-model:hasSecondProp",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ziOT-nhmQiqvCV8LSxAyHA",
        resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
    )
    expected = Oap(resource_oap=expected_res_oap, value_oaps=[expected_val_oap])
    res = _get_oap_of_one_resource(resource, config)
    assert res == expected


def test_get_oaps_of_one_kb_resclass_0_results() -> None:
    dsp_client = Mock(spec=DspClient)
    dsp_client.get = Mock(return_value={})
    res = _get_oaps_of_one_kb_resclass(dsp_client, "proj_iri", "resclass")
    assert res == []
    assert len(dsp_client.get.call_args_list) == 1
    called_route = dsp_client.get.call_args_list[0].args[0]
    assert called_route.startswith("/v2/searchextended/")
    assert "proj_iri" in called_route
    assert "resclass" in called_route


def test_get_oaps_of_one_kb_resclass_1_result() -> None:
    pass


def test_get_oaps_of_one_kb_resclass_4_results_on_2_pages() -> None:
    pass
