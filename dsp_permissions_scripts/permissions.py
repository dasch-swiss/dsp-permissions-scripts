import json
from typing import Any
import requests
from dsp_permissions_scripts.models.permission import Doap, PermissionScope, DoapTarget
from dsp_permissions_scripts.models.value import ValueUpdate

from dsp_permissions_scripts.util import url_encode

KB_DOAP = "http://www.knora.org/ontology/knora-admin#DefaultObjectAccessPermission"


def __marshal_scope(scope: PermissionScope) -> dict[str, Any]:
    return {
        "additionalInformation": scope.info,
        "name": scope.name,
        "permissionCode": None
    }


def __marshal_scope_as_permission_string(scope: list[PermissionScope]) -> str:
    lookup: dict[str, list[str]] = {}
    for s in scope:
        p = lookup.get(s.name, [])
        p.append(s.info.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:"))
        lookup[s.name] = p
    strs = [f"{k} {','.join(l)}" for k, l in lookup.items()]
    return "|".join(strs)


def __get_scope(scope: dict[str, Any]) -> PermissionScope:
    return PermissionScope(
        info=scope["additionalInformation"],
        name=scope["name"]
    )


def make_scope(
    restricted_view: list[str] = [],
    view: list[str] = [],
    modify: list[str] = [],
    delete: list[str] = [],
    change_rights: list[str] = []
) -> list[PermissionScope]:
    res = []
    res.extend([PermissionScope(info=iri, name="RV") for iri in restricted_view])
    res.extend([PermissionScope(info=iri, name="V") for iri in view])
    res.extend([PermissionScope(info=iri, name="M") for iri in modify])
    res.extend([PermissionScope(info=iri, name="D") for iri in delete])
    res.extend([PermissionScope(info=iri, name="CR") for iri in change_rights])
    return res


def __get_doap(permission: dict[str, Any]) -> Doap:
    # print(permission)
    scope = [__get_scope(s) for s in permission["hasPermissions"]]
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


def get_doaps_for_project(project_iri: str, host: str, token: str) -> list[Doap]:
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = url_encode(project_iri)
    url = f"https://{host}/admin/permissions/doap/{project_iri}"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    doaps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
    doap_objects = [__get_doap(doap) for doap in doaps]
    return doap_objects


def get_permissions_for_project(project_iri: str, host: str, token: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    project_iri = url_encode(project_iri)
    url = f"https://{host}/admin/permissions/{project_iri}"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    permissions: list[dict[str, Any]] = response.json()["permissions"]
    return permissions


def update_all_doap_scopes_for_project(project_iri: str, scope: list[PermissionScope], host: str, token: str) -> None:
    doaps = get_doaps_for_project(project_iri, host, token)
    for d in doaps:
        print(d.iri, d.target, d.scope)
        update_doap_scope(d.iri, scope, host, token)


def update_doap_scope(permission_iri: str, scope: list[PermissionScope], host: str, token: str) -> None:
    iri = url_encode(permission_iri)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{host}/admin/permissions/{iri}/hasPermissions"
    payload = {"hasPermissions": [__marshal_scope(s) for s in scope]}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 200
    print(response.json())


def update_permissions_for_resources_and_values(resource_iris: list[str], scope: list[PermissionScope], host: str, token: str) -> None:
    for iri in resource_iris:
        update_permissions_for_resource_and_values(iri, scope, host, token)


def update_permissions_for_resource_and_values(resource_iri: str,  scope: list[PermissionScope], host: str, token: str) -> None:
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
        scope: list[PermissionScope],
        host: str,
        token: str
) -> None:
    payload = {
        "@id": resource_iri,
        "@type": type_,
        "knora-api:hasPermissions": __marshal_scope_as_permission_string(scope),
        "@context": context
    }
    if lmd:
        payload["knora-api:lastModificationDate"] = lmd
    url = f"https://{host}/v2/resources"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 200
    print(f"Updated permissions for {resource_iri}")


def update_permissions_for_value(
        resource_iri: str,
        value: ValueUpdate,
        resource_type: str,
        context: dict[str, str],
        scope: list[PermissionScope],
        host: str,
        token: str
) -> None:
    print(value.value_iri)
    payload = {
        "@id": resource_iri,
        "@type": resource_type,
        value.property: {
            "@id": value.value_iri,
            "@type": value.value_type,
            "knora-api:hasPermissions": __marshal_scope_as_permission_string(scope)
        },
        "@context": context
    }
    url = f"https://{host}/v2/values"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 400 and response.text:
        if "dsp.errors.BadRequestException: The submitted permissions are the same as the current ones" in response.text:
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
    res: list[ValueUpdate] = []
    for k, v in resource.items():
        if k in {"@id", "@type", "@context", "rdfs:label"}:
            continue
        match v:
            case {"@id": id_, "@type": type_, **properties} if "/values/" in id_ and "knora-api:hasPermissions" in properties:
                res.append(ValueUpdate(k, id_, type_))
            case _:
                continue
    return res


def __get_resource(resource_iri: str, host: str, token: str) -> dict[str, Any]:
    iri = url_encode(resource_iri)
    url = f"https://{host}/v2/resources/{iri}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    return data


def __get_lmd(resource: dict[str, Any]) -> str | None:
    return resource.get("knora-api:lastModificationDate")


def __get_type(resource: dict[str, Any]) -> str:
    t: str = resource["@type"]
    return t


def __get_context(resource: dict[str, Any]) -> dict[str, str]:
    c: dict[str, str] = resource["@context"]
    return c
