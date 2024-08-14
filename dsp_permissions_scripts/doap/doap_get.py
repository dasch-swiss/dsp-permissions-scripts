from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import EntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_and_onto_iris_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_admin_route_object

logger = get_logger(__name__)


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
    target: GroupDoapTarget | EntityDoapTarget
    match permission:
        case {"forProject": project_iri, "forGroup": group}:
            target = GroupDoapTarget(project_iri=project_iri, group=Group(val=group))
        case {"forProject": project_iri, **p}:
            target = EntityDoapTarget(
                project_iri=project_iri, resource_class=p.get("forResourceClass"), property=p.get("forProperty")
            )
    return Doap(
        target=target,
        scope=scope,
        doap_iri=permission["iri"],
    )


def get_doaps_of_project(shortcode: str, dsp_client: DspClient) -> list[Doap]:
    """
    Returns the DOAPs for a project.
    Optionally, select only the DOAPs that are related to either a group, or a resource class, or a property.
    By default, all DOAPs are returned, regardless of their target (target=all).
    """
    logger.info("****** Retrieving all DOAPs... ******")
    project_iri, _ = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    doaps = _get_all_doaps_of_project(project_iri, dsp_client)
    msg = f"Retrieved {len(doaps)} DOAPs"
    logger.info(msg)
    return doaps
