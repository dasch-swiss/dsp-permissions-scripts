from dataclasses import dataclass
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.models.value import ValueUpdate
from dsp_permissions_scripts.oap.oap_set import (
    _get_resource,
    _get_values_to_update,
    _update_permissions_for_value,
)
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AffectedResource:
    res_iri: str
    val_iri: str
    prop_iri: str


def _get_affected_resources(host: str) -> list[AffectedResource]:
    affected_resources: list[AffectedResource] = [
        AffectedResource(
            "http://rdfh.ch/0102/WiFqK8SwTN6a74ioeHWPsQ",
            "http://rdfh.ch/0102/WiFqK8SwTN6a74ioeHWPsQ/values/82yjg3sETmGtflJnwjrJYg",
            f"http://{host}/ontology/0102/scenario-tanner/v2#correspondenceHasAuthorValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/8zpaTce4RDyhUS3h5GilVQ",
            "http://rdfh.ch/0102/8zpaTce4RDyhUS3h5GilVQ/values/WSJFMezeQBWUU4kXDVpKJA",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/FORXi9-YQYe-s2S99MwiBg",
            "http://rdfh.ch/0102/FORXi9-YQYe-s2S99MwiBg/values/i9unif3TSaK5l_xedCHdmg",
            f"http://{host}/ontology/knora-api/v2#hasStillImageFileValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/Ys4ib1s3RIK-fjmJ8Issww",
            "http://rdfh.ch/0102/Ys4ib1s3RIK-fjmJ8Issww/values/u4wxGYXZQgi-4ws-wQFhiw",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/ZVhmsPc6R6ikEbOayTbXgQ",
            "http://rdfh.ch/0102/ZVhmsPc6R6ikEbOayTbXgQ/values/BNnbMePSS1ybgMWISztRbA",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/bOyXLSH9Q6aGcIKZ3tMfrw",
            "http://rdfh.ch/0102/bOyXLSH9Q6aGcIKZ3tMfrw/values/da8ADzMWS3ekUoYxw0bU-g",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/pUQQVfX2Qvq7eTVKeJrFYQ",
            "http://rdfh.ch/0102/pUQQVfX2Qvq7eTVKeJrFYQ/values/2jiozpbdSrO0KO-VuET_NQ",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/w8uEnv6_QHGJg-Pd6oh6Jg",
            "http://rdfh.ch/0102/w8uEnv6_QHGJg-Pd6oh6Jg/values/1LRVS8J_SFC3PoYTAQXBKA",
            f"http://{host}/ontology/0102/scenario-tanner/v2#isPartOfDocumentValue",
        ),
        AffectedResource(
            "http://rdfh.ch/0102/O_QdkkzASTmdutPo_H2uEQ",
            "http://rdfh.ch/0102/O_QdkkzASTmdutPo_H2uEQ/values/3YG-PJhAQkeEzsRS8RMYMA",
            f"http://{host}/ontology/0102/scenario-tanner/v2#hasBirthDate",
        ),
    ]
    return affected_resources


def _assert_contested_value_exists(
    affected_resources: list[AffectedResource],
    host: str,
    token: str,
) -> None:
    for aff_res in affected_resources:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://{host}/v2/resources/{quote_plus(aff_res.res_iri)}"
        response_as_json = requests.get(url=url, headers=headers, timeout=10).json()
        
        if "scenario-tanner" in aff_res.prop_iri:
            prop_short = aff_res.prop_iri.replace(
                f"http://{host}/ontology/0102/scenario-tanner/v2#", "scenario-tanner:"
            )
        elif "knora-api" in aff_res.prop_iri:
            prop_short = aff_res.prop_iri.replace(f"http://{host}/ontology/knora-api/v2#", "knora-api:")
        
        if response_as_json[prop_short]["@type"] == "knora-api:LinkValue": 
            assert aff_res.val_iri == response_as_json[prop_short]["@id"]
        else:
            assert aff_res.val_iri.endswith(response_as_json[prop_short]["knora-api:valueHasUUID"])
    

def _get_new_scope() -> PermissionScope:
    scope = PermissionScope.create(
        CR=["http://www.knora.org/ontology/knora-admin#ProjectAdmin"],
        D=["http://www.knora.org/ontology/knora-admin#Creator"],
        M=[],
        V=["http://www.knora.org/ontology/knora-admin#ProjectMember"],
        RV=[
            "http://www.knora.org/ontology/knora-admin#UnknownUser",
            "http://www.knora.org/ontology/knora-admin#KnownUser"
        ],
    )
    return scope


def _get_params_for_update(
    affected_resource: AffectedResource,
    host: str,
    token: str,
) -> tuple[str, str, dict[str, str]]:
    resource = _get_resource(affected_resource.res_iri, host, token)
    resource_type: str = resource["@type"]
    context: dict[str, str] = resource["@context"]
    affected_value = [x for x in _get_values_to_update(resource) if x.value_iri == affected_resource.val_iri][0]
    return resource_type, affected_value.value_type, context


def _update_permissions_for_affected_value(
    affected_resource: AffectedResource,
    host: str,
    token: str,
) -> None:
    resource_type, value_type, context = _get_params_for_update(affected_resource, host, token)
    scope = _get_new_scope()
    _update_permissions_for_value(
        resource_iri=affected_resource.res_iri,
        value=ValueUpdate(affected_resource.prop_iri, affected_resource.val_iri, value_type),
        resource_type=resource_type,
        context=context,
        scope=scope,
        host=host,
        token=token,
    )


def cleanup_tanner() -> None:
    """
    As can be seen in project_data/0102/resources affected by dsp.errors.NotFoundException.txt,
    and project_data/0102/occurrences of dsp.errors.NotFoundException.log,
    some resources raised a NotFoundException when trying to access one of their values.
    This script cleans this up.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("stage")
    token = login(host)

    affected_resources = _get_affected_resources(host)
    _assert_contested_value_exists(
        affected_resources=affected_resources,
        host=host, 
        token=token,
    )
    for aff_res in affected_resources:
        _update_permissions_for_affected_value(
            affected_resource=aff_res,
            host=host,
            token=token,
        )


if __name__ == "__main__":
    cleanup_tanner()
