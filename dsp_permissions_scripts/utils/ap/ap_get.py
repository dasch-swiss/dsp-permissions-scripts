
from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.ap import Ap, ApValue
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode

logger = get_logger(__name__)


def _create_ap_from_admin_route_response(permission: dict[str, Any]) -> Ap:
    """Deserializes a AP from JSON as returned by /admin/permissions/ap/{project_iri}"""
    ap = Ap(
        forGroup=permission["forGroup"],
        forProject=permission["forProject"],
        hasPermissions=frozenset(ApValue(p["name"]) for p in permission["hasPermissions"]),
        iri=permission["iri"],
    )
    return ap


def _get_all_aps_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[Ap]:
    """Returns all Administrative Permissions of the given project."""
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/ap/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    aps: list[dict[str, Any]] = response.json()["administrative_permissions"]
    ap_objects = [_create_ap_from_admin_route_response(ap) for ap in aps]
    return ap_objects


def _filter_aps_by_group(
    aps: list[Ap],
    forGroup: str,
) -> Ap:
    aps = [ap for ap in aps if ap.forGroup == forGroup]
    assert len(aps) == 1
    return aps[0]


def _delete_single_ap(
    ap: Ap,
    host: str,
    token: str,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    ap_iri = quote_plus(ap.iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{ap_iri}"
    response = requests.delete(url, headers=headers, timeout=5)
    assert response.status_code == 200
    logger.info(f"Deleted Administrative Permission {ap.iri} on host {host}")


def delete_ap(
    host: str,
    token: str,
    existing_aps: list[Ap],
    forGroup: str,
) -> list[Ap]:
    """Deletes the Administrative Permission of a group."""
    logger.info(f"Deleting the Administrative Permission for group {forGroup} on server {host}")
    ap_to_delete = _filter_aps_by_group(
        aps=existing_aps,
        forGroup=forGroup,
    )
    _delete_single_ap(
        ap=ap_to_delete,
        host=host,
        token=token,
    )
    existing_aps.remove(ap_to_delete)
    return existing_aps


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
