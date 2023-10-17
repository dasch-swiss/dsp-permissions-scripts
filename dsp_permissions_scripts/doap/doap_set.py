import warnings
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.doap.doap_get import create_doap_from_admin_route_response
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
)

logger = get_logger(__name__)


def _update_doap_scope(
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
    response = requests.put(url, headers=headers, json=payload, timeout=10)
    if response.status_code != 200:
        raise ApiError( f"Could not update scope of DOAP {doap_iri}", response.text, response.status_code, payload)
    new_doap = create_doap_from_admin_route_response(response.json()["default_object_access_permission"])
    return new_doap


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
    if not doaps:
        warnings.warn(f"There are no DOAPs to update on {host}")
        return
    logger.info(f"Updating {len(doaps)} DOAPs on {host}...")
    print(f"Updating {len(doaps)} DOAPs on {host}...")
    for d in doaps:
        try:
            _ = _update_doap_scope(
                doap_iri=d.doap_iri,
                scope=d.scope,
                host=host,
                token=token,
            )
            logger.info(f"Successfully updated DOAP {d.doap_iri}")
        except ApiError as err:
            logger.error(err)
            warnings.warn(err.message)
