from typing import Any, cast

from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.helpers import sort_groups


def create_string_from_scope(perm_scope: PermissionScope) -> str:
    """Serializes a permission scope to a permissions string as used by /v2 routes."""
    as_dict = {}
    for perm_letter, groups in perm_scope.model_dump(mode="json").items():
        groups = cast(list[dict[str, str]], groups)
        if groups:
            as_dict[perm_letter] = sort_groups([Group(val=g) for _dict in groups for g in _dict.values()])
    strs = [f"{k} {','.join([x.val for x in l])}" for k, l in as_dict.items()]
    return "|".join(strs)


def create_scope_from_string(permission_string: str) -> PermissionScope:
    """Deserializes a permission string as used by /v2 routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    scopes = permission_string.split("|")
    for scope in scopes:
        perm_letter, groups_as_str = scope.split(" ")
        groups = groups_as_str.split(",")
        groups = [g.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#") for g in groups]
        kwargs[perm_letter] = groups
    return PermissionScope.from_dict(kwargs)


def create_scope_from_admin_route_object(admin_route_object: list[dict[str, Any]]) -> PermissionScope:
    """Deserializes an object returned by /admin/permissions routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    for obj in admin_route_object:
        attr_name: str = obj["name"]
        group: str = obj["additionalInformation"]
        group = group.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#")
        if attr_name in kwargs:
            kwargs[attr_name].append(group)
        else:
            kwargs[attr_name] = [group]
    return PermissionScope.from_dict(kwargs)


def create_admin_route_object_from_scope(perm_scope: PermissionScope) -> list[dict[str, str | None]]:
    """Serializes a permission scope to an object that can be used for requests to /admin/permissions routes."""
    scope_elements: list[dict[str, str | None]] = []
    for perm_letter, groups in perm_scope.model_dump(mode="json").items():
        groups = cast(list[dict[str, str]], groups)
        for group in groups:
            scope_elements.append(
                {
                    "additionalInformation": group["val"],
                    "name": perm_letter,
                    "permissionCode": None,
                }
            )
    return scope_elements
