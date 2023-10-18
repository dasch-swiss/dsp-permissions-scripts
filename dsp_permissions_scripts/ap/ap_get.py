from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode
from dsp_permissions_scripts.utils.try_request import http_call_with_retry

logger = get_logger(__name__)


def create_ap_from_admin_route_object(permission: dict[str, Any]) -> Ap:
    """Deserializes a AP from JSON as returned by /admin/permissions/ap/{project_iri}"""
    ap = Ap(
        forGroup=permission["forGroup"],
        forProject=permission["forProject"],
        hasPermissions=frozenset(ApValue(p["name"]) for p in permission["hasPermissions"]),
        iri=permission["iri"],
    )
    return ap


def create_admin_route_object_from_ap(ap: Ap) -> dict[str, Any]:
    """Serializes a AP to JSON as expected by /admin/permissions/ap/{project_iri}"""
    has_permissions = [
        {"additionalInformation": None, "name": p.value, "permissionCode": None} for p in ap.hasPermissions
    ]
    ap_dict = {
        "forGroup": ap.forGroup,
        "forProject": ap.forProject,
        "hasPermissions": has_permissions,
        "iri": ap.iri,
    }
    return ap_dict


def _get_all_aps_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[Ap]:
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/ap/{project_iri}"
    response = http_call_with_retry(
        action=lambda: requests.get(url, headers=headers, timeout=10),
        err_msg=f"Could not get APs of project {project_iri}",
    )
    if response.status_code != 200:
        raise ApiError(f"Could not get APs of project {project_iri}", response.text, response.status_code)
    aps: list[dict[str, Any]] = response.json()["administrative_permissions"]
    ap_objects = [create_ap_from_admin_route_object(ap) for ap in aps]
    return ap_objects


def get_aps_of_project(
    host: str,
    shortcode: str,
    token: str,
) -> list[Ap]:
    """Returns the Administrative Permissions for a project."""
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    aps = _get_all_aps_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    print(f"Retrieved {len(aps)} Administrative Permissions of project {shortcode} on server {host}")
    logger.info(f"Retrieved {len(aps)} Administrative Permissions of project {shortcode} on server {host}")
    return aps
