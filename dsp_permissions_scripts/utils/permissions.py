import json
from typing import Any, Sequence
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.permission import (
    Doap,
    DoapTarget,
    DoapTargetType,
    PermissionScopeElement,
)
from dsp_permissions_scripts.models.value import ValueUpdate
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode

KB_DOAP = "http://www.knora.org/ontology/knora-admin#DefaultObjectAccessPermission"

# TODO: maybe these methods should live on the PermissionScopeElement model?


def __marshal_scope(scope_element: PermissionScopeElement) -> dict[str, Any]:
    """
    Serializes a permission scope element to a dict
    in the shape that it can be used for JSON requests to /admin/permissions routes.
    """
    return {
        "additionalInformation": scope_element.info,
        "name": scope_element.name,
        "permissionCode": None,
    }


def __marshal_scope_as_permission_string(scope: list[PermissionScopeElement]) -> str:
    """
    Serializes a permission scope to a permissions string as used by /v2 routes.
    """
    lookup: dict[str, list[str]] = {}
    for s in scope:
        p = lookup.get(s.name, [])
        p.append(str(s.info).replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:"))
        lookup[s.name] = p
    strs = [f"{k} {','.join(l)}" for k, l in lookup.items()]
    return "|".join(strs)


def __get_scope_element(scope: dict[str, Any]) -> PermissionScopeElement:
    """
    turns permissions JSON  as returned by /admin/permissions routes into a PermissionScopeElement object.
    """
    return PermissionScopeElement(
        info=scope["additionalInformation"],
        name=scope["name"],
    )


def __get_doap(permission: dict[str, Any]) -> Doap:
    """
    Deserializes a DOAP from JSON as returned by /admin/permissions/doap/{project_iri}
    """
    scope = [__get_scope_element(s) for s in permission["hasPermissions"]]
    doap = Doap(
        target=DoapTarget(
            project=permission["forProject"],
            group=permission["forGroup"],
            resource_class=permission["forResourceClass"],
            property=permission["forProperty"],
        ),
        scope=scope,
        iri=permission["iri"],
    )
    return doap


def get_doaps_for_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[Doap]:
    """
    Returns all DOAPs for the given project.
    """
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = quote_plus(project_iri, safe="")
    url = f"https://{host}/admin/permissions/doap/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    doaps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
    doap_objects = [__get_doap(doap) for doap in doaps]
    return doap_objects


def get_doaps_of_groups(
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
    all_doaps = get_doaps_for_project(
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


def filter_doaps_by_target(
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
    url = f"https://{host}/admin/permissions/{project_iri}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    permissions: list[dict[str, Any]] = response.json()["permissions"]
    return permissions


def update_doap_scope(
    permission_iri: str,
    scope: list[PermissionScopeElement],
    host: str,
    token: str,
) -> Doap:
    """
    Updates the scope of the given DOAP.
    """
    iri = quote_plus(permission_iri, safe="")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{host}/admin/permissions/{iri}/hasPermissions"
    payload = {"hasPermissions": [__marshal_scope(s) for s in scope]}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    assert response.status_code == 200
    new_doap = __get_doap(response.json()["default_object_access_permission"])
    return new_doap


def update_permissions_for_resources_and_values(
    resource_iris: list[str],
    scope: list[PermissionScopeElement],
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given resources and their values.
    """
    for iri in resource_iris:
        update_permissions_for_resource_and_values(iri, scope, host, token)


def update_permissions_for_resource_and_values(
    resource_iri: str,
    scope: list[PermissionScopeElement],
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given resource and its values.
    """
    print(f"Updating permissions for {resource_iri}...")
    resource = __get_resource(resource_iri, host, token)
    lmd = __get_lmd(resource)
    type_ = __get_type(resource)
    context = __get_context(resource)
    values = __get_value_iris(resource)
    update_permissions_for_resource(resource_iri, lmd, type_, context, scope, host, token)
    for v in values:
        update_permissions_for_value(resource_iri, v, type_, context, scope, host, token)
    print("Done. \n")


def update_permissions_for_resource(
    resource_iri: str,
    lmd: str | None,
    type_: str,
    context: dict[str, str],
    scope: list[PermissionScopeElement],
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given resource.
    """
    payload = {
        "@id": resource_iri,
        "@type": type_,
        "knora-api:hasPermissions": __marshal_scope_as_permission_string(scope),
        "@context": context,
    }
    if lmd:
        payload["knora-api:lastModificationDate"] = lmd
    url = f"https://{host}/v2/resources"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    assert response.status_code == 200
    print(f"Updated permissions for {resource_iri}")


def update_permissions_for_value(
    resource_iri: str,
    value: ValueUpdate,
    resource_type: str,
    context: dict[str, str],
    scope: list[PermissionScopeElement],
    host: str,
    token: str,
) -> None:
    """
    Updates the permissions for the given value.
    """
    print(value.value_iri)
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        value.property: {
            "@id": value.value_iri,
            "@type": value.value_type,
            "knora-api:hasPermissions": __marshal_scope_as_permission_string(scope),
        },
        "@context": context,
    }
    url = f"https://{host}/v2/values"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload, timeout=5)
    if response.status_code == 400 and response.text:
        if (
            "dsp.errors.BadRequestException: "
            "The submitted permissions are the same as the current ones" in response.text
        ):
            print(f"Permissions for {value.value_iri} are already up to date")
            return
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        print(resource_iri, value.value_iri)
        print(json.dumps(payload, indent=4))
        print("!!!!!")
        print()
        return
        # raise Exception(f"Error updating permissions for {value.value_iri}")
    print(f"Updated permissions for {value.value_iri}")


def __get_value_iris(resource: dict[str, Any]) -> list[ValueUpdate]:
    """
    Returns a list of values that have permissions and hence should be updated.
    """
    res: list[ValueUpdate] = []
    for k, v in resource.items():
        if k in {"@id", "@type", "@context", "rdfs:label"}:
            continue
        match v:
            case {
                "@id": id_,
                "@type": type_,
                **properties,
            } if "/values/" in id_ and "knora-api:hasPermissions" in properties:
                res.append(ValueUpdate(k, id_, type_))
            case _:
                continue
    return res


def __get_resource(
    resource_iri: str,
    host: str,
    token: str,
) -> dict[str, Any]:
    """
    Requests the resource with the given IRI from the API.
    """
    iri = quote_plus(resource_iri, safe="")
    url = f"https://{host}/v2/resources/{iri}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    return data


def __get_lmd(resource: dict[str, Any]) -> str | None:
    """
    Gets last modification date from a resource JSON-LD dict.
    """
    return resource.get("knora-api:lastModificationDate")


def __get_type(resource: dict[str, Any]) -> str:
    """
    Gets the type from a resource JSON-LD dict."""
    t: str = resource["@type"]
    return t


def __get_context(resource: dict[str, Any]) -> dict[str, str]:
    """
    Gets the context object from a resource JSON-LD dict.
    """
    c: dict[str, str] = resource["@context"]
    return c
