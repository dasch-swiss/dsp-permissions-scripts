import itertools
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.errors import PermissionsAlreadyUpToDate
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import ModifiedOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.scope_serialization import create_string_from_scope

logger = get_logger(__name__)


def update_permissions_for_value(
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


def update_permissions_for_resource(  # noqa: PLR0913
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


def _update_batch(batch: tuple[ModifiedOap, ...], dsp_client: DspClient) -> list[str]:
    failed_iris = []
    for oap in batch:
        res_iri = oap.resource_oap.resource_iri if oap.resource_oap else oap.value_oaps[0].resource_iri
        try:
            resource = dsp_client.get(f"/v2/resources/{quote_plus(res_iri, safe='')}")
        except ApiError as exc:
            logger.error(
                f"Cannot update resource {res_iri}. "
                f"The resource cannot be retrieved for the following reason: {exc.message}"
            )
            failed_iris.append(res_iri)
            continue
        if oap.resource_oap:
            try:
                update_permissions_for_resource(
                    resource_iri=oap.resource_oap.resource_iri,
                    lmd=resource.get("knora-api:lastModificationDate"),
                    resource_type=resource["@type"],
                    context=resource["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                    scope=oap.resource_oap.scope,
                    dsp_client=dsp_client,
                )
            except ApiError as err:
                logger.error(err)
                failed_iris.append(oap.resource_oap.resource_iri)
        for val_oap in oap.value_oaps:
            try:
                update_permissions_for_value(
                    resource_iri=val_oap.resource_iri,
                    value=val_oap,
                    resource_type=resource["@type"],
                    context=resource["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                    dsp_client=dsp_client,
                )
            except ApiError as err:
                logger.error(err)
                failed_iris.append(val_oap.value_iri)
    return failed_iris


def _write_failed_iris_to_file(
    failed_iris: list[str],
    shortcode: str,
    server: str,
    filename: str,
) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        msg = f"Problems occurred while updating the OAPs of these resources (project {shortcode}, server {server}):\n"
        f.write(msg)
        f.write("\n".join(failed_iris))


def _launch_thread_pool(oaps: list[ModifiedOap], nthreads: int, dsp_client: DspClient) -> list[str]:
    all_failed_iris: list[str] = []
    with ThreadPoolExecutor(max_workers=nthreads) as pool:
        jobs = [pool.submit(_update_batch, batch, dsp_client) for batch in itertools.batched(oaps, 100)]
        for result in as_completed(jobs):
            failed_iris = result.result()
            all_failed_iris.extend(failed_iris)
    return all_failed_iris


def apply_updated_oaps_on_server(
    oaps: list[ModifiedOap],
    shortcode: str,
    dsp_client: DspClient,
    nthreads: int = 4,
) -> None:
    """
    Applies modified Object Access Permissions of resources (and their values) on a DSP server.
    Don't forget to set a number of threads that doesn't overload the server.
    """
    oaps = [oap for oap in oaps if oap.resource_oap or oap.value_oaps]
    if not oaps:
        logger.warning(f"There are no OAPs to update on {dsp_client.server}")
        return
    value_oap_count = sum(len(oap.value_oaps) for oap in oaps)
    res_oap_count = sum(1 if oap.resource_oap else 0 for oap in oaps)
    msg = f"Updating {res_oap_count} resource OAPs and {value_oap_count} value OAPs on {dsp_client.server}..."
    logger.info(f"******* {msg} *******")

    failed_iris = _launch_thread_pool(oaps, nthreads, dsp_client)
    if failed_iris:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"FAILED_RESOURCES_AND_VALUES_{timestamp}.txt"
        _write_failed_iris_to_file(
            failed_iris=sorted(failed_iris),
            shortcode=shortcode,
            server=dsp_client.server,
            filename=filename,
        )
        msg = f"ERROR: {len(failed_iris)} resources or values could not be updated. They were written to {filename}."
        logger.error(msg)
    msg = f"Updated {res_oap_count} resource OAPs and {value_oap_count} value OAPs on {dsp_client.server}... *******"
    logger.info(msg)
