from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import (
    get_project_iri_and_onto_iris_by_shortcode,
)

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


def _get_all_aps_of_project(project_iri: str, dsp_client: DspClient) -> list[Ap]:
    project_iri = quote_plus(project_iri, safe="")
    try:
        response = dsp_client.get(f"/admin/permissions/ap/{project_iri}")
    except ApiError as err:
        err.message = f"Could not get APs of project {project_iri}"
        raise err from None
    aps: list[dict[str, Any]] = response["administrative_permissions"]
    ap_objects = [create_ap_from_admin_route_object(ap) for ap in aps]
    return ap_objects


def get_aps_of_project(shortcode: str, dsp_client: DspClient) -> list[Ap]:
    """Returns the Administrative Permissions for a project."""
    logger.info("****** Retrieving all Administrative Permissions... ******")
    project_iri, _ = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    aps = _get_all_aps_of_project(project_iri, dsp_client)
    logger.info(f"Retrieved {len(aps)} Administrative Permissions")
    return aps
