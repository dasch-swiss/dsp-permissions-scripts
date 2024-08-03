from typing import Any
from unittest.mock import Mock
from urllib.parse import quote

import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap import oap_get
from dsp_permissions_scripts.oap.oap_get import KB_RESCLASSES
from dsp_permissions_scripts.oap.oap_get import _get_oap_of_one_resource
from dsp_permissions_scripts.oap.oap_get import _get_oaps_of_one_kb_resclass
from dsp_permissions_scripts.oap.oap_get import get_oaps_of_kb_resclasses
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


@pytest.fixture()
def gravsearch_1_link_obj() -> dict[str, Any]:
    return {
        "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember",
        "@type": "knora-api:LinkObj",
        "@id": "http://rdfh.ch/0806/5moPQcfeS0mfhh-Oed3tPA",
    }


@pytest.fixture()
def gravsearch_4_link_objs_on_2_pages() -> list[dict[str, Any]]:
    page_1 = {
        "@graph": [
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember",
                "@type": "knora-api:LinkObj",
                "@id": "http://rdfh.ch/0806/5moPQcfeS0mfhh-Oed3tPA",
            },
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember",
                "@type": "knora-api:LinkObj",
                "@id": "http://rdfh.ch/0806/8DGe7ai1TFmyTD0XN56ubg",
            },
        ],
        "knora-api:mayHaveMoreResults": True,
    }
    page_2 = {
        "@graph": [
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember",
                "@type": "knora-api:LinkObj",
                "@id": "http://rdfh.ch/0806/BmnN7X_zR7C0f7B4ibAZ6A",
            },
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember",
                "@type": "knora-api:LinkObj",
                "@id": "http://rdfh.ch/0806/_n8QtGaXTVG14jtYU5H33Q",
            },
        ]
    }
    return [page_1, page_2]


@pytest.fixture()
def video_segment() -> dict[str, Any]:  # https://ark.stage.dasch.swiss/ark:/72163/1/0812/l32ehsHuTfaQAKVTRiuBRAR
    return {
        "knora-api:hasSegmentBounds": {
            "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@type": "knora-api:IntervalValue",
            "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA/values/vBYk7HEERHWNMy0IagG97A",
        },
        "knora-api:relatesToValue": {
            "knora-api:linkValueHasTarget": {
                "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
                "@type": "ekws:Agent",
                "@id": "http://rdfh.ch/0812/DUB459kJWDmO8o_GyvQJMg",
            },
            "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@type": "knora-api:LinkValue",
            "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA/values/stMJC52VRYSAJEI_bllNmQ",
        },
        "knora-api:hasTitle": {
            "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@type": "knora-api:TextValue",
            "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA/values/ggBMLia9Q-iZFzj5T1zsgg",
        },
        "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
        "knora-api:isVideoSegmentOfValue": {
            "knora-api:linkValueHasTarget": {
                "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
                "@type": "ekws:MovingImageRepresentation",
                "@id": "http://rdfh.ch/0812/eIsPNAgNQLCoczIkuos9zw",
            },
            "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@type": "knora-api:LinkValue",
            "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA/values/eylWw-RCQOOdircrcfCzFA",
        },
        "@type": "knora-api:VideoSegment",
        "knora-api:hasDescription": {
            "knora-api:hasPermissions": "CR knora-admin:Creator|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA/values/WP1q4naiTty1CEcv9cglaA",
            "@type": "knora-api:TextValue",
        },
        "@id": "http://rdfh.ch/0812/l32ehsHuTfaQAKVTRiuBRA",
    }


@pytest.fixture()
def linkobj() -> dict[str, Any]:  # https://app.test.dasch.swiss/resource/F18E/Os_5VvgkSC2saUlSUdcLhA
    return {
        "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
        "@type": "knora-api:LinkObj",
        "knora-api:hasLinkToValue": [
            {
                "knora-api:linkValueHasTarget": {
                    "knora-api:hasPermissions": "V knora-admin:KnownUser|RV knora-admin:UnknownUser",
                    "@type": "invalid-jwt-token:DocumentRepresentation",
                    "@id": "http://rdfh.ch/F18E/1ft22XVzQ1Gk2eYMvybhGA",
                },
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
                "@type": "knora-api:LinkValue",
                "@id": "http://rdfh.ch/F18E/Os_5VvgkSC2saUlSUdcLhA/values/YlwXFucHSVq5VfETR3dc0Q",
            },
            {
                "knora-api:linkValueHasTarget": {
                    "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
                    "@type": "invalid-jwt-token:DocumentRepresentation",
                    "@id": "http://rdfh.ch/F18E/3BlLqRdlRZCpYcGzTlK8Iw",
                },
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
                "@type": "knora-api:LinkValue",
                "@id": "http://rdfh.ch/F18E/Os_5VvgkSC2saUlSUdcLhA/values/yUA0UsnBReuYJ8zmQjvG3A",
            },
        ],
        "@id": "http://rdfh.ch/F18E/Os_5VvgkSC2saUlSUdcLhA",
        "knora-api:hasComment": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser",
            "@type": "knora-api:TextValue",
            "@id": "http://rdfh.ch/F18E/Os_5VvgkSC2saUlSUdcLhA/values/TGyIeaV2QBqxAl8NxCs_Vw",
        },
    }


def test_that_uses_video_segment(video_segment: dict[str, Any]) -> None:
    pytest.fail(f"Please write a test for {video_segment}")


def test_that_uses_linkobj(linkobj: dict[str, Any]) -> None:
    pytest.fail(f"Please write a test for {linkobj}")


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


class Test_get_oaps_of_one_kb_resclass:
    def test_get_oaps_of_one_kb_resclass_0_results(self) -> None:
        dsp_client = Mock(spec=DspClient)
        dsp_client.get = Mock(side_effect=[{}])
        res = _get_oaps_of_one_kb_resclass(dsp_client, "proj_iri", "resclass")
        assert res == []
        assert len(dsp_client.get.call_args_list) == 1
        called_route = dsp_client.get.call_args_list[0].args[0]
        assert called_route.startswith("/v2/searchextended/")
        assert "proj_iri" in called_route
        assert "resclass" in called_route
        assert quote("OFFSET 0", safe="") in called_route

    def test_get_oaps_of_one_kb_resclass_1_result(self, gravsearch_1_link_obj: dict[str, Any]) -> None:
        dsp_client = Mock(spec=DspClient)
        dsp_client.get = Mock(side_effect=[gravsearch_1_link_obj])
        res = _get_oaps_of_one_kb_resclass(dsp_client, "proj_iri", "resclass")
        expected = Oap(
            resource_oap=ResourceOap(
                scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], D=[group.PROJECT_MEMBER]),
                resource_iri="http://rdfh.ch/0806/5moPQcfeS0mfhh-Oed3tPA",
            ),
            value_oaps=[],
        )
        assert res == [expected]

    def test_get_oaps_of_one_kb_resclass_4_results_on_2_pages(
        self,
        gravsearch_4_link_objs_on_2_pages: list[dict[str, Any]],
    ) -> None:
        dsp_client = Mock(spec=DspClient)
        dsp_client.get = Mock(side_effect=gravsearch_4_link_objs_on_2_pages)
        res = _get_oaps_of_one_kb_resclass(dsp_client, "proj_iri", "resclass")
        expected_scope = PermissionScope.create(CR=[group.PROJECT_ADMIN], D=[group.PROJECT_MEMBER])
        expected_res_oaps = [
            ResourceOap(scope=expected_scope, resource_iri="http://rdfh.ch/0806/5moPQcfeS0mfhh-Oed3tPA"),
            ResourceOap(scope=expected_scope, resource_iri="http://rdfh.ch/0806/8DGe7ai1TFmyTD0XN56ubg"),
            ResourceOap(scope=expected_scope, resource_iri="http://rdfh.ch/0806/BmnN7X_zR7C0f7B4ibAZ6A"),
            ResourceOap(scope=expected_scope, resource_iri="http://rdfh.ch/0806/_n8QtGaXTVG14jtYU5H33Q"),
        ]
        expected = [Oap(resource_oap=res_oap, value_oaps=[]) for res_oap in expected_res_oaps]
        assert res == expected

        assert len(dsp_client.get.call_args_list) == 2  # noqa: PLR2004 (magic value used in comparison)
        called_route_1 = dsp_client.get.call_args_list[0].args[0]
        called_route_2 = dsp_client.get.call_args_list[1].args[0]
        assert quote("OFFSET 0", safe="") in called_route_1
        assert quote("OFFSET 1", safe="") in called_route_2


class Test_get_oaps_of_kb_resclasses:
    def test_get_oaps_of_kb_resclasses_all_resclasses_all_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="all",
            retrieve_values="all",
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(dsp_client, "proj_iri", KB_RESCLASSES)
        oap_get._enrich_with_value_oaps.assert_called_once_with(dsp_client, ["res_only_oap_1", "res_only_oap_2"])

    def test_get_oaps_of_kb_resclasses_all_resclasses_specified_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="all",
            retrieve_values="specified_props",
            specified_props=["onto:prop_1", "onto:prop_2"],
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(dsp_client, "proj_iri", KB_RESCLASSES)
        oap_get._enrich_with_value_oaps.assert_called_once_with(
            dsp_client, ["res_only_oap_1", "res_only_oap_2"], ["onto:prop_1", "onto:prop_2"]
        )

    def test_get_oaps_of_kb_resclasses_all_resclasses_no_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="all",
            retrieve_values="none",
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(dsp_client, "proj_iri", KB_RESCLASSES)
        oap_get._enrich_with_value_oaps.assert_not_called()

    def test_get_oaps_of_kb_resclasses_some_resclasses_all_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="specified_res_classes",
            specified_res_classes=["knora-api:Region", "custom-onto:foo"],
            retrieve_values="all",
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(
            dsp_client, "proj_iri", ["knora-api:Region"]
        )
        oap_get._enrich_with_value_oaps.assert_called_once_with(dsp_client, ["res_only_oap_1", "res_only_oap_2"])

    def test_get_oaps_of_kb_resclasses_some_resclasses_some_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="specified_res_classes",
            specified_res_classes=["knora-api:Region", "custom-onto:foo"],
            retrieve_values="specified_props",
            specified_props=["onto:prop_1", "onto:prop_2"],
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(
            dsp_client, "proj_iri", ["knora-api:Region"]
        )
        oap_get._enrich_with_value_oaps.assert_called_once_with(
            dsp_client, ["res_only_oap_1", "res_only_oap_2"], ["onto:prop_1", "onto:prop_2"]
        )

    def test_get_oaps_of_kb_resclasses_some_resclasses_no_values(self) -> None:
        oap_get._get_oaps_of_specified_kb_resclasses = Mock(side_effect=[["res_only_oap_1", "res_only_oap_2"]])
        oap_get._enrich_with_value_oaps = Mock(side_effect=[["enriched_oap_1", "enriched_oap_2"]])
        dsp_client = Mock(spec=DspClient)
        oap_config = OapRetrieveConfig(
            retrieve_resources="specified_res_classes",
            specified_res_classes=["knora-api:Region", "custom-onto:foo"],
            retrieve_values="none",
        )
        _ = get_oaps_of_kb_resclasses(dsp_client, "proj_iri", oap_config)
        oap_get._get_oaps_of_specified_kb_resclasses.assert_called_once_with(
            dsp_client, "proj_iri", ["knora-api:Region"]
        )
        oap_get._enrich_with_value_oaps.assert_not_called()
