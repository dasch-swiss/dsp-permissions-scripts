import json
from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.doap import Oap
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.models.value import ValueUpdate
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope

logger = get_logger(__name__)


def _get_value_iris(resource: dict[str, Any]) -> list[ValueUpdate]:
    """
    Returns a list of values that have permissions and hence should be updated.
    """
    res: list[ValueUpdate] = []
    for k, v in resource.items():
        if k in {"@id", "@type", "@context", "rdfs:label"}:
            continue
        match v:
            case {
                "@id": id_,
                "@type": type_,
                **properties,
            } if "/values/" in id_ and "knora-api:hasPermissions" in properties:
                res.append(ValueUpdate(k, id_, type_))
            case _:
                continue
    return res


def _get_resource(
    resource_iri: str,
    host: str,
    token: str,
) -> dict[str, Any]:
    """
    Requests the resource with the given IRI from the API.
    """
    iri = quote_plus(resource_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/resources/{iri}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    return data


def _get_lmd(resource: dict[str, Any]) -> str | None:
    """
    Gets last modification date from a resource JSON-LD dict.
    """
    return resource.get("knora-api:lastModificationDate")


def _get_type(resource: dict[str, Any]) -> str:
    """
    Gets the type from a resource JSON-LD dict."""
    t: str = resource["@type"]
    return t


def _get_context(resource: dict[str, Any]) -> dict[str, str]:
    """
    Gets the context object from a resource JSON-LD dict.
    """
    c: dict[str, str] = resource["@context"]
    return c


def _update_permissions_for_value(
    resource_iri: str,
    value: ValueUpdate,
    resource_type: str,
    context: dict[str, str],
    scope: PermissionScope,
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given value.
    """
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        value.property: {
            "@id": value.value_iri,
            "@type": value.value_type,
            "knora-api:hasPermissions": create_string_from_scope(scope),
        },
        "@context": context,
    }
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/values"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    if response.status_code == 400 and response.text:
        already = "dsp.errors.BadRequestException: The submitted permissions are the same as the current ones"
        if already in response.text:
            msg = f"Permissions of resource {resource_iri}, value {value.value_iri} are already up to date"
            logger.warning(msg)
    elif response.status_code != 200:
        logger.error(
            f"Error while updating permissions of resource {resource_iri}, value {value.value_iri}. "
            f"Response status code: {response.status_code}. "
            f"Response text: {response.text}. "
            f"Payload: {json.dumps(payload, indent=4)}"
        )
    else:
        logger.info(f"Updated permissions of resource {resource_iri}, value {value.value_iri}")


def _update_permissions_for_resource(
    resource_iri: str,
    lmd: str | None,
    resource_type: str,
    context: dict[str, str],
    scope: PermissionScope,
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given resource.
    """
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        "knora-api:hasPermissions": create_string_from_scope(scope),
        "@context": context,
    }
    if lmd:
        payload["knora-api:lastModificationDate"] = lmd
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/resources"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    assert response.status_code == 200
    logger.info(f"Updated permissions of resource {resource_iri}")


def _update_permissions_for_resource_and_values(
    resource_iri: str,
    scope: PermissionScope,
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given resource and its values.
    """
    resource = _get_resource(resource_iri, host, token)
    lmd = _get_lmd(resource)
    resource_type = _get_type(resource)
    context = _get_context(resource)
    values = _get_value_iris(resource)
    _update_permissions_for_resource(
        resource_iri=resource_iri, 
        lmd=lmd, 
        resource_type=resource_type, 
        context=context, 
        scope=scope, 
        host=host, 
        token=token,
    )
    for v in values:
        _update_permissions_for_value(
            resource_iri=resource_iri, 
            value=v, 
            resource_type=resource_type, 
            context=context, 
            scope=scope, 
            host=host, 
            token=token,
        )


def apply_updated_oaps_on_server(
    resource_oaps: list[Oap],
    host: str,
    token: str,
) -> None:
    """Applies object access permissions on a DSP server."""
    logger.info("******* Applying updated object access permissions on server *******")
    print(f"{get_timestamp()}: ******* Applying updated object access permissions on server *******")
    for index, resource_oap in enumerate(resource_oaps):
        msg = f"Updating permissions of resource {index + 1}/{len(resource_oaps)}: {resource_oap.object_iri}..."
        logger.info("=====")
        logger.info(msg)
        print(f"{get_timestamp()}: {msg}")
        _update_permissions_for_resource_and_values(
            resource_iri=resource_oap.object_iri,
            scope=resource_oap.scope,
            host=host,
            token=token,
        )
        logger.info(f"Updated permissions of resource {resource_oap.object_iri} and its values.")
