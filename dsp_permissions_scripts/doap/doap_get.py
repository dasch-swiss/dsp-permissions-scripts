from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import DoapTarget
from dsp_permissions_scripts.doap.doap_model import DoapTargetType
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import (
    get_project_iri_and_onto_iris_by_shortcode,
)
from dsp_permissions_scripts.utils.scope_serialization import (
    create_scope_from_admin_route_object,
)

logger = get_logger(__name__)


def _filter_doaps_by_target(
    doaps: list[Doap],
    target: DoapTargetType,
) -> list[Doap]:
    """
    Returns only the DOAPs that are related to either a group, or a resource class, or a property.
    In case of "all", return all DOAPs.
    """
    match target:
        case DoapTargetType.ALL:
            filtered_doaps = doaps
        case DoapTargetType.GROUP:
            filtered_doaps = [d for d in doaps if d.target.group]
        case DoapTargetType.PROPERTY:
            filtered_doaps = [d for d in doaps if d.target.property]
        case DoapTargetType.RESOURCE_CLASS:
            filtered_doaps = [d for d in doaps if d.target.resource_class]
    return filtered_doaps


def _get_all_doaps_of_project(project_iri: str, dsp_client: DspClient) -> list[Doap]:
    project_iri = quote_plus(project_iri, safe="")
    try:
        response = dsp_client.get(f"/admin/permissions/doap/{project_iri}")
    except ApiError as err:
        err.message = f"Error while getting DOAPs of project {project_iri}"
        raise err from None
    doaps: list[dict[str, Any]] = response["default_object_access_permissions"]
    doap_objects = [create_doap_from_admin_route_response(doap) for doap in doaps]
    return doap_objects


def create_doap_from_admin_route_response(permission: dict[str, Any]) -> Doap:
    """Deserializes a DOAP from JSON as returned by /admin/permissions/doap/{project_iri}"""
    scope = create_scope_from_admin_route_object(permission["hasPermissions"])
    doap = Doap(
        target=DoapTarget(
            project=permission["forProject"],
            group=Group(val=permission["forGroup"]),
            resource_class=permission["forResourceClass"],
            property=permission["forProperty"],
        ),
        scope=scope,
        doap_iri=permission["iri"],
    )
    return doap


def get_doaps_of_project(
    shortcode: str,
    dsp_client: DspClient,
    target_type: DoapTargetType = DoapTargetType.ALL,
) -> list[Doap]:
    """
    Returns the DOAPs for a project.
    Optionally, select only the DOAPs that are related to either a group, or a resource class, or a property.
    By default, all DOAPs are returned, regardless of their target (target=all).
    """
    logger.info("****** Retrieving all DOAPs... ******")
    project_iri, _ = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    doaps = _get_all_doaps_of_project(project_iri, dsp_client)
    filtered_doaps = _filter_doaps_by_target(
        doaps=doaps,
        target=target_type,
    )
    msg = f"Retrieved {len(doaps)} DOAPs"
    if target_type != DoapTargetType.ALL:
        msg += f", {len(filtered_doaps)} of which are related to {target_type}."
    logger.info(msg)
    return filtered_doaps
