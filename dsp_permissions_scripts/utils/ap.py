
from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode

logger = get_logger(__name__)

def _get_all_aps_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[Ap]:
    """
    Returns all Administrative Permissions of the given project.
    """
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/doap/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    aps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
    ap_objects = [create_ap_from_admin_route_response(ap) for ap in aps]
    return ap_objects


def get_aps_of_project(
    host: str,
    shortcode: str,
    token: str,
) -> list[Ap]:
    """Returns the Administrative Permissions for a project."""
    logger.info(f"******* Getting Administrative Permissions of project {shortcode} on server {host} *******")
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    aps = _get_all_aps_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    logger.info(f"Found {len(aps)} Administrative Permissions")
    return aps
