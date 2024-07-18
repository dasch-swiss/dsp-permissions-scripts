import itertools
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.errors import PermissionsAlreadyUpToDate
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import get_resource
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_PREFIX
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope

logger = get_logger(__name__)


def _update_permissions_for_value(
    resource_iri: str,
    value: ValueOap,
    resource_type: str,
    context: dict[str, str],
    dsp_client: DspClient,
) -> None:
    """Updates the permissions for the given value (of a property) on a DSP server"""
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        value.property: {
            "@id": value.value_iri,
            "@type": value.value_type,
            "knora-api:hasPermissions": create_string_from_scope(value.scope),
        },
        "@context": context,
    }
    try:
        dsp_client.put("/v2/values", data=payload)
        logger.info(f"Updated permissions of resource {resource_iri}, value {value.value_iri}")
    except PermissionsAlreadyUpToDate:
        logger.warning(f"Permissions of resource {resource_iri}, value {value.value_iri} are already up to date")
    except ApiError as err:
        err.message = f"Error while updating permissions of resource {resource_iri}, value {value.value_iri}"
        raise err from None


def _update_permissions_for_resource(  # noqa: PLR0913
    resource_iri: str,
    lmd: str | None,
    resource_type: str,
    context: dict[str, str],
    scope: PermissionScope,
    dsp_client: DspClient,
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
        dsp_client.put("/v2/resources", data=payload)
        logger.info(f"Updated permissions of resource {resource_iri}")
    except PermissionsAlreadyUpToDate:
        logger.warning(f"Permissions of resource {resource_iri} are already up to date")
    except ApiError as err:
        err.message = f"ERROR while updating permissions of resource {resource_iri}"
        raise err from None


def _update_batch(batch: tuple[ResourceOap | ValueOap, ...], dsp_client: DspClient) -> list[str]:
    failed_iris = []
    for oap in batch:
        try:
            resource = get_resource(oap.resource_iri, dsp_client)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Cannot update resource {oap.resource_iri}: {exc}")
            failed_iris.append(oap.resource_iri)
            continue
        if isinstance(oap, ResourceOap):
            try:
                _update_permissions_for_resource(
                    resource_iri=oap.resource_iri,
                    lmd=resource.get("knora-api:lastModificationDate"),
                    resource_type=resource["@type"],
                    context=resource["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_PREFIX},
                    scope=oap.scope,
                    dsp_client=dsp_client,
                )
            except ApiError as err:
                logger.error(err)
                failed_iris.append(oap.resource_iri)
        elif isinstance(oap, ValueOap):
            try:
                _update_permissions_for_value(
                    resource_iri=oap.resource_iri,
                    value=oap,
                    resource_type=resource["@type"],
                    context=resource["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_PREFIX},
                    dsp_client=dsp_client,
                )
            except ApiError as err:
                logger.error(err)
                failed_iris.append(oap.value_iri)
        else:
            raise ValueError(f"The provided OAP is neither a resource OAP nor a value OAP: {oap}")
    return failed_iris


def _write_failed_iris_to_file(
    failed_iris: list[str],
    shortcode: str,
    host: str,
    filename: str,
) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Problems occurred while updating the OAPs of these resources (project {shortcode}, host {host}):\n")
        f.write("\n".join(failed_iris))


def _launch_thread_pool(oaps: list[ResourceOap | ValueOap], nthreads: int, dsp_client: DspClient) -> list[str]:
    all_failed_iris: list[str] = []
    with ThreadPoolExecutor(max_workers=nthreads) as pool:
        jobs = [pool.submit(_update_batch, batch, dsp_client) for batch in itertools.batched(oaps, 100)]
        for result in as_completed(jobs):
            failed_iris = result.result()
            all_failed_iris.extend(failed_iris)
    return all_failed_iris


def apply_updated_oaps_on_server(
    oaps: list[ResourceOap | ValueOap],
    host: str,
    shortcode: str,
    dsp_client: DspClient,
    nthreads: int = 4,
) -> None:
    """
    Applies modified Object Access Permissions of resources (and their values) on a DSP server.
    Don't forget to set a number of threads that doesn't overload the server.
    """
    if not oaps:
        logger.warning(f"There are no OAPs to update on {host}")
        return
    value_oap_count = sum(isinstance(oap, ValueOap) for oap in oaps)
    res_oap_count = sum(isinstance(oap, ResourceOap) for oap in oaps)
    logger.info(f"******* Updating {res_oap_count} resource OAPs and {value_oap_count} value OAPs on {host}... *******")

    failed_iris = _launch_thread_pool(oaps, nthreads, dsp_client)
    if failed_iris:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"FAILED_RESOURCES_AND_VALUES_{timestamp}.txt"
        _write_failed_iris_to_file(
            failed_iris=sorted(failed_iris),
            shortcode=shortcode,
            host=host,
            filename=filename,
        )
        msg = f"ERROR: {len(failed_iris)} resources or values could not be updated. They were written to {filename}."
        logger.error(msg)
    logger.info(f"Updated OAPs of {len(oaps)} resources on {host}")
