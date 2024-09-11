from typing import Any
from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap import update_iris
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.oap.update_iris import IRIUpdater
from dsp_permissions_scripts.oap.update_iris import ResourceIRIUpdater
from dsp_permissions_scripts.oap.update_iris import ValueIRIUpdater
from dsp_permissions_scripts.utils.dsp_client import DspClient


@pytest.fixture()
def res_dict_2_props() -> dict[str, Any]:
    return {
        "knora-api:lastModificationDate": {"@value": "2024-09-10T18:07:10.753289758Z", "@type": "xsd:dateTimeStamp"},
        "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
        "@type": "testonto:CompoundThing",
        "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
        "testonto:hasSimpleText": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
            "@type": "knora-api:TextValue",
            "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/FWSVNZFJRai8-4OQu5pU8Q",
        },
        "testonto:hasOtherText": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
            "@type": "knora-api:TextValue",
            "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/4bf-72HPTXSUdTxY8udGew",
        },
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "testonto": "http://0.0.0.0:3333/ontology/4123/testonto/v2#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
    }


@pytest.fixture()
def res_dict_2_vals() -> dict[str, Any]:
    return {
        "knora-api:lastModificationDate": {"@value": "2024-09-10T18:07:10.753289758Z", "@type": "xsd:dateTimeStamp"},
        "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
        "@type": "testonto:CompoundThing",
        "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
        "testonto:hasSimpleText": [
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
                "@type": "knora-api:TextValue",
                "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/4bf-72HPTXSUdTxY8udGew",
            },
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:UnknownUser",
                "@type": "knora-api:TextValue",
                "@id": "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/FWSVNZFJRai8-4OQu5pU8Q",
            },
        ],
        "@context": {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "testonto": "http://0.0.0.0:3333/ontology/4123/testonto/v2#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
    }


def test_factory_with_res_iri() -> None:
    dsp_client: DspClient = Mock()
    res_iri = "http://rdfh.ch/4123/2ETqDXKeRrS5JSd6TxFO5g"
    result = IRIUpdater.from_string(res_iri, dsp_client)
    assert isinstance(result, ResourceIRIUpdater)
    assert result.iri == res_iri


def test_factory_with_value_iri() -> None:
    dsp_client: DspClient = Mock()
    val_iri = "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fkw"
    result = IRIUpdater.from_string(val_iri, dsp_client)
    assert isinstance(result, ValueIRIUpdater)
    assert result.iri == val_iri


def test_factory_with_invalid_iri() -> None:
    dsp_client: DspClient = Mock()
    invalid_iris = [
        "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fk",
        "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWx",
    ]
    for inv in invalid_iris:
        with pytest.raises(InvalidIRIError):
            IRIUpdater.from_string(inv, dsp_client)


def test_ResourceIRIUpdater(res_dict_2_props: dict[str, Any]) -> None:
    dsp_client = Mock(spec_set=DspClient, get=Mock(return_value=res_dict_2_props))
    update_iris.update_permissions_for_resource = Mock()  # type: ignore[attr-defined]
    new_scope = PermissionScope.create(D=[PROJECT_ADMIN])
    res_iri = "http://rdfh.ch/4123/2ETqDXKeRrS5JSd6TxFO5g"
    IRIUpdater.from_string(res_iri, dsp_client).update_iri(new_scope)
    dsp_client.get.assert_called_once_with("/v2/resources/http%3A%2F%2Frdfh.ch%2F4123%2F2ETqDXKeRrS5JSd6TxFO5g")
    update_iris.update_permissions_for_resource.assert_called_once_with(  # type: ignore[attr-defined]
        resource_iri=res_iri,
        lmd=res_dict_2_props["knora-api:lastModificationDate"],
        resource_type=res_dict_2_props["@type"],
        context=res_dict_2_props["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
        scope=new_scope,
        dsp_client=dsp_client,
    )


def test_ValueIRIUpdater_2_props(res_dict_2_props: dict[str, Any]) -> None:
    dsp_client = Mock(spec_set=DspClient, get=Mock(return_value=res_dict_2_props))
    update_iris.update_permissions_for_value = Mock()  # type: ignore[attr-defined]
    val_oap = ValueOap(
        scope=PermissionScope.create(D=[PROJECT_ADMIN]),
        property="testonto:hasOtherText",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/4bf-72HPTXSUdTxY8udGew",
        resource_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
    )
    IRIUpdater.from_string(val_oap.value_iri, dsp_client).update_iri(val_oap.scope)
    dsp_client.get.assert_called_once_with("/v2/resources/http%3A%2F%2Frdfh.ch%2F4123%2FQDdiwk_3Rk--N2dzsSPOdw")
    update_iris.update_permissions_for_value.assert_called_once_with(  # type: ignore[attr-defined]
        resource_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
        value=val_oap,
        resource_type=res_dict_2_props["@type"],
        context=res_dict_2_props["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
        dsp_client=dsp_client,
    )


def test_ValueIRIUpdater_2_vals(res_dict_2_vals: dict[str, Any]) -> None:
    dsp_client = Mock(spec_set=DspClient, get=Mock(return_value=res_dict_2_vals))
    update_iris.update_permissions_for_value = Mock()  # type: ignore[attr-defined]
    val_oap = ValueOap(
        scope=PermissionScope.create(D=[PROJECT_ADMIN]),
        property="testonto:hasSimpleText",
        value_type="knora-api:TextValue",
        value_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/4bf-72HPTXSUdTxY8udGew",
        resource_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
    )
    IRIUpdater.from_string(val_oap.value_iri, dsp_client).update_iri(val_oap.scope)
    dsp_client.get.assert_called_once_with("/v2/resources/http%3A%2F%2Frdfh.ch%2F4123%2FQDdiwk_3Rk--N2dzsSPOdw")
    update_iris.update_permissions_for_value.assert_called_once_with(  # type: ignore[attr-defined]
        resource_iri="http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw",
        value=val_oap,
        resource_type=res_dict_2_vals["@type"],
        context=res_dict_2_vals["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
        dsp_client=dsp_client,
    )


def test_ValueIRIUpdater_invalid_iri(res_dict_2_vals: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    """test what happens if a value IRI is provided that is not part of the current resource"""
    dsp_client = Mock(spec_set=DspClient, get=Mock(return_value=res_dict_2_vals))
    update_iris.update_permissions_for_value = Mock()  # type: ignore[attr-defined]
    val_iri = "http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw/values/eD0ii5mIS9y18M6fMy1Fkw"
    IRIUpdater.from_string(val_iri, dsp_client).update_iri(PermissionScope.create(D=[PROJECT_ADMIN]))
    dsp_client.get.assert_called_once_with("/v2/resources/http%3A%2F%2Frdfh.ch%2F4123%2FQDdiwk_3Rk--N2dzsSPOdw")
    update_iris.update_permissions_for_value.assert_not_called()  # type: ignore[attr-defined]
    assert len(caplog.records) == 1
    log_msg_expected = f"Could not find value {val_iri} in resource http://rdfh.ch/4123/QDdiwk_3Rk--N2dzsSPOdw"
    assert caplog.records[0].message == log_msg_expected
