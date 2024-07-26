from typing import Any

from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.utils.helpers import sort_groups


def create_string_from_scope(perm_scope: PermissionScope) -> str:
    """Serializes a permission scope to a permissions string as used by /v2 routes."""
    as_dict = {}
    for perm_letter in perm_scope.model_fields:
        if groups := perm_scope.get(perm_letter):
            as_dict[perm_letter] = sort_groups(groups)
    strs = [f"{k} {','.join([x.val for x in v])}" for k, v in as_dict.items()]
    return "|".join(strs)


def create_scope_from_string(permission_string: str) -> PermissionScope:
    """Deserializes a permission string as used by /v2 routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    scopes = permission_string.split("|")
    for scope in scopes:
        perm_letter, groups_as_str = scope.split(" ")
        groups = groups_as_str.split(",")
        kwargs[perm_letter] = [g.replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:") for g in groups]
    return PermissionScope.from_dict(kwargs)


def create_scope_from_admin_route_object(admin_route_object: list[dict[str, Any]]) -> PermissionScope:
    """Deserializes an object returned by /admin/permissions routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    for obj in admin_route_object:
        attr_name: str = obj["name"]
        group: str = obj["additionalInformation"].replace(KNORA_ADMIN_ONTO_NAMESPACE, "knora-admin:")
        if attr_name in kwargs:
            kwargs[attr_name].append(group)
        else:
            kwargs[attr_name] = [group]
    return PermissionScope.from_dict(kwargs)


def create_admin_route_object_from_scope(perm_scope: PermissionScope) -> list[dict[str, str | None]]:
    """
    Serializes a permission scope to an object that can be used for requests to /admin/permissions routes.
    Note: This route doesn't accept relative IRIs.
    """
    scope_elements: list[dict[str, str | None]] = []
    for perm_letter in perm_scope.model_fields:
        groups = perm_scope.get(perm_letter)
        for group in groups:
            scope_elements.append(
                {
                    "additionalInformation": group.val.replace("knora-admin:", KNORA_ADMIN_ONTO_NAMESPACE),
                    "name": perm_letter,
                    "permissionCode": None,
                }
            )
    return scope_elements
