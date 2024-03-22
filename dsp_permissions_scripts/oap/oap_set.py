# pylint: disable=too-many-arguments

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.models.value import ValueUpdate
from dsp_permissions_scripts.oap.oap_get import get_resource
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope
from dsp_permissions_scripts.utils import connection

logger = get_logger(__name__)


def _get_values_to_update(resource: dict[str, Any]) -> list[ValueUpdate]:
    """Returns a list of values that have permissions and hence should be updated."""
    res: list[ValueUpdate] = []
    for k, v in resource.items():
        if k in {"@id", "@type", "@context", "rdfs:label", "knora-api:DeletedValue"}:
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


def _update_permissions_for_value(
    resource_iri: str,
    value: ValueUpdate,
    resource_type: str,
    context: dict[str, str],
    scope: PermissionScope,
) -> None:
    """Updates the permissions for the given value (of a property) on a DSP server"""
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
    try:
        connection.con.put("/v2/values", data=payload)
    except ApiError as err:
        err.message = f"Error while updating permissions of resource {resource_iri}, value {value.value_iri}"
        raise err from None
    logger.info(f"Updated permissions of resource {resource_iri}, value {value.value_iri}")


def _update_permissions_for_resource(
    resource_iri: str,
    lmd: str | None,
    resource_type: str,
    context: dict[str, str],
    scope: PermissionScope,
    host: str,
) -> None:
    """Updates the permissions for the given resource on a DSP server"""
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        "knora-api:hasPermissions": create_string_from_scope(scope),
        "@context": context,
    }
    if lmd:
        payload["knora-api:lastModificationDate"] = lmd
    try:
        connection.con.put("/v2/resources", data=payload)
    except ApiError as err:
        err.message = f"ERROR while updating permissions of resource {resource_iri}"
        raise err from None
    logger.info(f"Updated permissions of resource {resource_iri}")


def _update_permissions_for_resource_and_values(
    resource_iri: str,
    scope: PermissionScope,
    host: str,
) -> tuple[str, bool]:
    """Updates the permissions for the given resource and its values on a DSP server"""
    try:
        resource = get_resource(resource_iri)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(f"Cannot update resource {resource_iri}: {exc}")
        warnings.warn(f"Cannot update resource {resource_iri}: {exc}")
        return resource_iri, False
    values = _get_values_to_update(resource)
    
    success = True
    try:
        _update_permissions_for_resource(
            resource_iri=resource_iri,
            lmd=resource.get("knora-api:lastModificationDate"),
            resource_type=resource["@type"],
            context=resource["@context"],
            scope=scope,
            host=host,
        )
    except ApiError as err:
        logger.error(err)
        warnings.warn(err.message)
        success = False
    
    for v in values:
        try:
            _update_permissions_for_value(
                resource_iri=resource_iri,
                value=v,
                resource_type=resource["@type"],
                context=resource["@context"],
                scope=scope,
            )
        except ApiError as err:
            logger.error(err)
            warnings.warn(err.message)
            success = False
    
    return resource_iri, success


def _write_failed_res_iris_to_file(
    failed_res_iris: list[str],
    shortcode: str,
    host: str,
    filename: str,
) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Problems occurred while updating the OAPs of these resources (project {shortcode}, host {host}):\n")
        f.write("\n".join(failed_res_iris))


def _launch_thread_pool(
    resource_oaps: list[Oap],
    host: str,
    nthreads: int,
) -> list[str]:
    counter = 0
    total = len(resource_oaps)
    failed_res_iris: list[str] = []
    with ThreadPoolExecutor(max_workers=nthreads) as pool:
        jobs = [
            pool.submit(
                _update_permissions_for_resource_and_values,
                resource_oap.object_iri,
                resource_oap.scope,
                host,
            ) for resource_oap in resource_oaps
        ]
        for result in as_completed(jobs):
            resource_iri, success = result.result()
            counter += 1
            if not success:
                failed_res_iris.append(resource_iri)
                logger.info(f"Failed updating resource {counter}/{total} ({resource_iri}) and its values.")
                print(f"Failed updating resource {counter}/{total} ({resource_iri}) and its values.")
            else:
                logger.info(f"Updated resource {counter}/{total} ({resource_iri}) and its values.")
                print(f"Updated resource {counter}/{total} ({resource_iri}) and its values.")
    return failed_res_iris


def apply_updated_oaps_on_server(
    resource_oaps: list[Oap],
    host: str,
    shortcode: str,
    nthreads: int = 4,
) -> None:
    """
    Applies modified Object Access Permissions of resources (and their values) on a DSP server.
    Don't forget to set a number of threads that doesn't overload the server.
    """
    if not resource_oaps:
        logger.warning(f"There are no OAPs to update on {host}")
        warnings.warn(f"There are no OAPs to update on {host}")
        return
    logger.info(f"******* Updating OAPs of {len(resource_oaps)} resources on {host} *******")
    print(f"******* Updating OAPs of {len(resource_oaps)} resources on {host} *******")

    failed_res_iris = _launch_thread_pool(resource_oaps, host, nthreads)

    if failed_res_iris:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"FAILED_RESOURCES_{timestamp}.txt"
        _write_failed_res_iris_to_file(
            failed_res_iris=failed_res_iris,
            shortcode=shortcode,
            host=host,
            filename=filename,
        )
        msg = (
            f"ERROR: {len(failed_res_iris)} resources could not (or only partially) be updated. "
            f"They were written to {filename}."
        )
        logger.error(msg)
        warnings.warn(msg)
