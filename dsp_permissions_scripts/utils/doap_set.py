from typing import Literal
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.permission import Doap
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.doap_get import create_doap_from_admin_route_response
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
)

logger = get_logger(__name__)

def __update_doap_scope(
    doap_iri: str,
    scope: PermissionScope,
    host: str,
    token: str,
) -> Doap:
    """
    Updates the scope of the given DOAP.
    """
    iri = quote_plus(doap_iri, safe="")
    headers = {"Authorization": f"Bearer {token}"}
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{iri}/hasPermissions"
    payload = {"hasPermissions": create_admin_route_object_from_scope(scope)}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    assert response.status_code == 200
    new_doap = create_doap_from_admin_route_response(response.json()["default_object_access_permission"])
    return new_doap


def __log_and_print_doap_update(
    doap: Doap,
    state: Literal["before", "after"],
) -> None:
    """
    Logs and prints the DOAP before or after the update.
    """
    heading = f"DOAP {state}:"
    body = doap.model_dump_json(indent=2)
    print(f"{heading}\n{'-' * len(heading)}\n{body}\n")
    logger.info(f"{heading}\n{body}")


def apply_updated_doaps_on_server(
    doaps: list[Doap],
    host: str,
    token: str,
) -> None:
    """
    Updates DOAPs on the server.

    Args:
        doaps: the DOAPs to be sent to the server
        host: the DSP server where the project is located
        token: the access token
    """
    logger.info(f"Updating {len(doaps)} DOAPs on {host}...")
    heading = f"{get_timestamp()}: Update {len(doaps)} DOAPs on {host}..."
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for d in doaps:
        __log_and_print_doap_update(doap=d, state="before")
        new_doap = __update_doap_scope(
            doap_iri=d.doap_iri,
            scope=d.scope,
            host=host,
            token=token,
        )
        __log_and_print_doap_update(doap=new_doap, state="after")
    print(f"{get_timestamp()}: All DOAPs have been updated.")