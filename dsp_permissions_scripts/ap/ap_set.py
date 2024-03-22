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
from dsp_permissions_scripts.utils.try_request import http_call_with_retry

logger = get_logger(__name__)


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
    response = http_call_with_retry(
        action=lambda: requests.put(url, headers=headers, json=payload, timeout=20),
        err_msg=f"Could not update Administrative Permission {ap.iri}",
    )
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
        return
    logger.info(f"Updating {len(aps)} APs on {host}...")
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
