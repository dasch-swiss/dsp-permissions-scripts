import copy
from typing import Any

from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.helpers import sort_groups


def create_string_from_scope(perm_scope: PermissionScope) -> str:
    """Serializes a permission scope to a permissions string as used by /v2 routes."""
    as_dict = {}
    for perm_letter, groups in perm_scope.model_dump(mode="json").items():
        if groups:
            as_dict[perm_letter] = sort_groups(groups)
    strs = [f"{k} {','.join(l)}" for k, l in as_dict.items()]
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
    return PermissionScope(**kwargs)  # type: ignore[arg-type]


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
    purged_kwargs = _remove_duplicates_from_kwargs_for_permission_scope(kwargs)
    return PermissionScope(**purged_kwargs)  # type: ignore[arg-type]


def _remove_duplicates_from_kwargs_for_permission_scope(kwargs: dict[str, list[str]]) -> dict[str, list[str]]:
    res = copy.deepcopy(kwargs)
    permissions = ["RV", "V", "M", "D", "CR"]
    permissions = [perm for perm in permissions if perm in kwargs]
    for perm in permissions:
        higher_permissions = permissions[permissions.index(perm) + 1 :] if perm != "CR" else []
        for group in kwargs[perm]:
            nested_list = [kwargs[hp] for hp in higher_permissions]
            flat_list = [y for x in nested_list for y in x]
            if flat_list.count(group) > 0:
                res[perm].remove(group)
    return res


def create_admin_route_object_from_scope(perm_scope: PermissionScope) -> list[dict[str, str | None]]:
    """Serializes a permission scope to an object that can be used for requests to /admin/permissions routes."""
    scope_elements: list[dict[str, str | None]] = []
    for perm_letter, groups in perm_scope.model_dump(mode="json").items():
        for group in groups:
            scope_elements.append(
                {
                    "additionalInformation": group,
                    "name": perm_letter,
                    "permissionCode": None,
                }
            )
    return scope_elements
