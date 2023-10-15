import warnings
from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.ap.ap_get import (
    create_admin_route_object_from_ap,
    create_ap_from_admin_route_object,
)
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp

logger = get_logger(__name__)


def _filter_aps_by_group(
    aps: list[Ap],
    forGroup: str,
) -> Ap:
    aps = [ap for ap in aps if ap.forGroup == forGroup]
    assert len(aps) == 1
    return aps[0]


def _delete_single_ap(
    ap: Ap,
    host: str,
    token: str,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    ap_iri = quote_plus(ap.iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{ap_iri}"
    response = requests.delete(url, headers=headers, timeout=5)
    if response.status_code != 200:
        raise ApiError(f"Could not delete Administrative Permission {ap.iri}", response.text, response.status_code)
    logger.info(f"Deleted Administrative Permission {ap.iri} on host {host}")


def _update_ap(
    ap: Ap,
    host: str,
    token: str,
) -> Ap:
    """
    Updates the given AP.
    """
    iri = quote_plus(ap.iri, safe="")
    headers = {"Authorization": f"Bearer {token}"}
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{iri}/hasPermissions"
    payload = {"hasPermissions": create_admin_route_object_from_ap(ap)["hasPermissions"]}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    if response.status_code != 200:
        raise ApiError(
            message=f"Could not update Administrative Permission {ap.iri}",
            response_text=response.text,
            status_code=response.status_code,
            payload=payload,
        )
    ap_updated: dict[str, Any] = response.json()["administrative_permission"]
    ap_object_updated = create_ap_from_admin_route_object(ap_updated)
    return ap_object_updated


def _log_and_print_ap_update(ap: Ap) -> None:
    """Logs and prints the AP after the update."""
    heading = "Updated AP as per response from server:"
    body = ap.model_dump_json(indent=2)
    print(f"{heading}\n{'-' * len(heading)}\n{body}\n")
    logger.info(f"{heading}\n{body}")


def apply_updated_aps_on_server(
    aps: list[Ap],
    host: str,
    token: str,
) -> None:
    """
    Updates APs on the server.

    Args:
        aps: the APs to be sent to the server
        host: the DSP server where the project is located
        token: the access token
    """
    logger.info(f"******* Updating {len(aps)} APs on {host} *******")
    heading = f"{get_timestamp()}: Updating {len(aps)} APs on {host}..."
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for ap in aps:
        try:
            new_ap = _update_ap(
                ap=ap,
                host=host,
                token=token,
            )
            _log_and_print_ap_update(ap=new_ap)
        except ApiError as err:
            logger.error(err)
            warnings.warn(err.message)

    print(f"{get_timestamp()}: All APs have been updated.")


def delete_ap(
    host: str,
    token: str,
    existing_aps: list[Ap],
    forGroup: str,
) -> list[Ap]:
    """Deletes the Administrative Permission of a group."""
    logger.info(f"Deleting the Administrative Permission for group {forGroup} on server {host}")
    ap_to_delete = _filter_aps_by_group(
        aps=existing_aps,
        forGroup=forGroup,
    )
    _delete_single_ap(
        ap=ap_to_delete,
        host=host,
        token=token,
    )
    existing_aps.remove(ap_to_delete)
    return existing_aps
