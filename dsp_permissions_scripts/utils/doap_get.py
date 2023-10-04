from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.permission import Doap, DoapTarget, DoapTargetType
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode
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


def _get_all_doaps_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[Doap]:
    """
    Returns all DOAPs of the given project.
    """
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/doap/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    doaps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
    doap_objects = [create_doap_from_admin_route_response(doap) for doap in doaps]
    return doap_objects


def create_doap_from_admin_route_response(permission: dict[str, Any]) -> Doap:
    """
    Deserializes a DOAP from JSON as returned by /admin/permissions/doap/{project_iri}
    """
    scope = create_scope_from_admin_route_object(permission["hasPermissions"])
    doap = Doap(
        target=DoapTarget(
            project=permission["forProject"],
            group=permission["forGroup"],
            resource_class=permission["forResourceClass"],
            property=permission["forProperty"],
        ),
        scope=scope,
        doap_iri=permission["iri"],
    )
    return doap


def get_doaps_of_project(
    host: str,
    shortcode: str,
    token: str,
    target: DoapTargetType = DoapTargetType.ALL,
) -> list[Doap]:
    """
    Returns the doaps for a project.
    Optionally, select only the DOAPs that are related to either a group, or a resource class, or a property.
    By default, all DOAPs are returned, regardless of their target (target=all).
    """
    logger.info(f"******* Getting DOAPs of project {shortcode} on server {host} *******")
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    doaps = _get_all_doaps_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    filtered_doaps = _filter_doaps_by_target(
        doaps=doaps,
        target=target,
    )
    logger.info(f"Found {len(doaps)} DOAPs, {len(filtered_doaps)} of which are related to {target}.")
    return filtered_doaps


def print_doaps_of_project(
    doaps: list[Doap],
    host: str,
    shortcode: str,
    target: DoapTargetType = DoapTargetType.ALL,
) -> None:
    heading = f"Project {shortcode} on server {host} has {len(doaps)} DOAPs"
    if target != DoapTargetType.ALL:
        heading += f" which are related to a {target}"
    print(f"\n{get_timestamp()}: {heading}\n{'=' * (len(heading) + len(get_timestamp()) + 2)}\n")
    logger.info(f"******* Printing DOAPs of project {shortcode} on server {host} *******")
    logger.info(heading)
    for d in doaps:
        representation = d.model_dump_json(indent=2, exclude_none=True)
        print(representation + "\n")
        logger.info(representation)
