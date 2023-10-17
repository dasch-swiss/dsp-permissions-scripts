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
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _delete_ap_on_server(
    ap: Ap,
    host: str,
    token: str,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    ap_iri = quote_plus(ap.iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{ap_iri}"
    response = requests.delete(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise ApiError(f"Could not delete Administrative Permission {ap.iri}", response.text, response.status_code)


def _update_ap_on_server(
    ap: Ap,
    host: str,
    token: str,
) -> Ap:
    iri = quote_plus(ap.iri, safe="")
    headers = {"Authorization": f"Bearer {token}"}
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{iri}/hasPermissions"
    payload = {"hasPermissions": create_admin_route_object_from_ap(ap)["hasPermissions"]}
    response = requests.put(url, headers=headers, json=payload, timeout=10)
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


def apply_updated_aps_on_server(
    aps: list[Ap],
    host: str,
    token: str,
) -> None:
    if not aps:
        logger.warning(f"There are no APs to update on {host}")
        warnings.warn(f"There are no APs to update on {host}")
        return
    logger.info(f"Updating {len(aps)} APs on {host}...")
    print(f"Updating {len(aps)} APs on {host}...")
    for ap in aps:
        try:
            _ = _update_ap_on_server(
                ap=ap,
                host=host,
                token=token,
            )
            logger.info(f"Successfully updated AP {ap.iri}")
        except ApiError as err:
            logger.error(err)
            warnings.warn(err.message)


def delete_ap_of_group_on_server(
    host: str,
    token: str,
    existing_aps: list[Ap],
    forGroup: str,
) -> list[Ap]:
    aps_to_delete = [ap for ap in existing_aps if ap.forGroup == forGroup]
    if not aps_to_delete:
        logger.warning(f"There are no APs to delete on {host} for group {forGroup}")
        warnings.warn(f"There are no APs to delete on {host} for group {forGroup}")
        return existing_aps
    print(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    logger.info(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    for ap in aps_to_delete:
        _delete_ap_on_server(
            ap=ap,
            host=host,
            token=token,
        )
        existing_aps.remove(ap)
        logger.info(f"Deleted Administrative Permission {ap.iri} on host {host}")
    return existing_aps
