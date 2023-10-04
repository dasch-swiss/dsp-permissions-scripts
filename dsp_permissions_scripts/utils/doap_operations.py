from typing import Any, Sequence
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import (
    Doap,
    DoapTarget,
    DoapTargetType,
    PermissionScope,
)
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
    create_scope_from_admin_route_object,
)


def __get_doap(permission: dict[str, Any]) -> Doap:
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


def __get_all_doaps_of_project(
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
    doap_objects = [__get_doap(doap) for doap in doaps]
    return doap_objects


def __get_doaps_of_groups(
    groups: Sequence[str | BuiltinGroup],
    host: str,
    shortcode: str,
    token: str,
) -> list[Doap]:
    """
    Retrieves the DOAPs for the given groups.

    Args:
        groups: the group IRIs to whose DOAP the scope should be applied
        host: the DSP server where the project is located
        shortcode: the shortcode of the project
        token: the access token

    Returns:
        applicable_doaps: the applicable DOAPs
    """
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    all_doaps = __get_all_doaps_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    groups_str = []
    for g in groups:
        groups_str.append(g.value if isinstance(g, BuiltinGroup) else g)
    applicable_doaps = [d for d in all_doaps if d.target.group in groups_str]
    assert len(applicable_doaps) == len(groups)
    return applicable_doaps


def __filter_doaps_by_target(
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


# TODO: this function is unused
def get_permissions_for_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[dict[str, Any]]:
    """
    Returns all permissions for the given project.
    """
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    permissions: list[dict[str, Any]] = response.json()["permissions"]
    return permissions


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
    new_doap = __get_doap(response.json()["default_object_access_permission"])
    return new_doap


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
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    doaps = __get_all_doaps_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    filtered_doaps = __filter_doaps_by_target(
        doaps=doaps,
        target=target,
    )
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
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for d in doaps:
        print(d.model_dump_json(indent=2, exclude_none=True))
        print()


def set_doaps_of_groups(
    scope: PermissionScope,
    groups: Sequence[str | BuiltinGroup],
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """
    Applies the given scope to the DOAPs of the given groups.

    Args:
        scope: one of the standard scopes defined in the Scope class
        groups: the group IRIs to whose DOAP the scope should be applied
        host: the DSP server where the project is located
        shortcode: the shortcode of the project
        token: the access token
    """
    applicable_doaps = __get_doaps_of_groups(
        groups=groups,
        host=host,
        shortcode=shortcode,
        token=token,
    )
    heading = f"Update {len(applicable_doaps)} DOAPs on {host}..."
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for d in applicable_doaps:
        print("Old DOAP:\n=========")
        print(d.model_dump_json(indent=2))
        new_doap = __update_doap_scope(
            doap_iri=d.doap_iri,
            scope=scope,
            host=host,
            token=token,
        )
        print("\nNew DOAP:\n=========")
        print(new_doap.model_dump_json(indent=2))
        print()
    print("All DOAPs have been updated.")
