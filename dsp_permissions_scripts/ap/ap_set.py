import warnings
from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.ap.ap_get import (
    create_admin_route_object_from_ap,
    create_ap_from_admin_route_object,
)
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils import dsp_client
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _update_ap_on_server(ap: Ap) -> Ap:
    iri = quote_plus(ap.iri, safe="")
    payload = {"hasPermissions": create_admin_route_object_from_ap(ap)["hasPermissions"]}
    try:
        response = dsp_client.dspClient.put(f"/admin/permissions/{iri}/hasPermissions", data=payload)
    except ApiError as err:
        err.message = f"Could not update Administrative Permission {ap.iri}"
        raise err from None
    ap_updated: dict[str, Any] = response["administrative_permission"]
    ap_object_updated = create_ap_from_admin_route_object(ap_updated)
    return ap_object_updated


def apply_updated_aps_on_server(aps: list[Ap], host: str) -> None:
    if not aps:
        logger.warning(f"There are no APs to update on {host}")
        warnings.warn(f"There are no APs to update on {host}")
        return
    logger.info(f"Updating {len(aps)} APs on {host}...")
    print(f"Updating {len(aps)} APs on {host}...")
    for ap in aps:
        try:
            _ = _update_ap_on_server(ap)
            logger.info(f"Successfully updated AP {ap.iri}")
        except ApiError as err:
            logger.error(err)
            warnings.warn(err.message)
