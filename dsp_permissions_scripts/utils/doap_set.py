


from typing import Sequence
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import Doap
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.doap_get import create_doap_from_admin_route_response, get_all_doaps_of_project
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import (
    create_admin_route_object_from_scope,
)


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
    all_doaps = get_all_doaps_of_project(
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
