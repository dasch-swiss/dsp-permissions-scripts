import warnings
from typing import Any, Literal
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.ap import Ap
from dsp_permissions_scripts.utils.ap.ap_get import (
    create_admin_route_object_from_ap,
    create_ap_from_admin_route_object,
)
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp

logger = get_logger(__name__)

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
    assert response.status_code == 200
    ap_updated: dict[str, Any] = response.json()["administrative_permission"]
    ap_object_updated = create_ap_from_admin_route_object(ap_updated)
    return ap_object_updated


def _log_and_print_ap_update(
    ap: Ap,
    state: Literal["before", "after"],
) -> None:
    """
    Logs and prints the AP before or after the update.
    """
    heading = f"AP {state}:"
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
        _log_and_print_ap_update(ap=ap, state="before")
        try:
            new_ap = _update_ap(
                ap=ap,
                host=host,
                token=token,
            )
            _log_and_print_ap_update(ap=new_ap, state="after")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.error(f"ERROR while updating Administrative Permission {ap.iri}", exc_info=True)
            warnings.warn(f"ERROR while updating Administrative Permission {ap.iri}")

    print(f"{get_timestamp()}: All APs have been updated.")
