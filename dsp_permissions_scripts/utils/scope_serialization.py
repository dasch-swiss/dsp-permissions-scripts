from typing import Any

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope


def create_string_from_scope(perm_scope: PermissionScope) -> str:
    """Serializes a permission scope to a permissions string as used by /v2 routes."""
    as_dict = {}
    for perm_letter, groups in perm_scope.model_dump().items():
        if groups:
            groups_as_str = [g.value if isinstance(g, BuiltinGroup) else g for g in groups]
            as_dict[perm_letter] = [
                g.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:") for g in groups_as_str
            ]
    strs = [f"{k} {','.join(l)}" for k, l in as_dict.items()]
    return "|".join(strs)


def create_scope_from_string(permission_string: str) -> PermissionScope:
    kwargs: dict[str, list[str]] = {}
    scopes = permission_string.split("|")
    for scope in scopes:
        perm_letter, groups_as_str = scope.split(" ")
        groups = groups_as_str.split(",")
        groups = [g.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#") for g in groups]
        kwargs[perm_letter] = groups
    return PermissionScope(**kwargs)  # type: ignore[arg-type]


    
def create_scope_from_admin_route_object(admin_route_object: list[dict[str, Any]]) -> PermissionScope:
    kwargs: dict[str, list[str]] = {}
    for obj in admin_route_object:
        attr_name: str = obj["name"]
        group: str = obj["additionalInformation"]
        group = group.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:")
        if attr_name in kwargs:
            kwargs[attr_name].append(group)
        else:
            kwargs[attr_name] = [group]
    return PermissionScope(**kwargs)  # type: ignore[arg-type]


def create_admin_route_object_from_scope(perm_scope: PermissionScope) -> list[dict[str, str | None]]:
    """Serializes a permission scope to a shape that can be used for requests to /admin/permissions routes."""
    scope_elements: list[dict[str, str | None]] = []
    for perm_letter, groups in perm_scope.model_dump().items():
        if groups:
            groups_as_str = [g.value if isinstance(g, BuiltinGroup) else g for g in groups]
            groups_as_str = [
                g.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:") for g in groups_as_str
            ]
            for group in groups_as_str:
                scope_elements.append(
                    {
                        "additionalInformation": group,
                        "name": perm_letter,
                        "permissionCode": None,
                }
            )
    return scope_elements
