from typing import Any

from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.group import sort_groups
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.dsp_client import DspClient


def create_string_from_scope(perm_scope: PermissionScope) -> str:
    """Serializes a permission scope to a permissions string as used by /v2 routes."""
    as_dict = {}
    for perm_letter in perm_scope.model_fields:
        if groups := perm_scope.get(perm_letter):
            as_dict[perm_letter] = sort_groups(groups)
    strs = [f"{k} {','.join([x.prefixed_iri for x in v])}" for k, v in as_dict.items()]
    return "|".join(strs)


def create_scope_from_string(permission_string: str, dsp_client: DspClient) -> PermissionScope:
    """Deserializes a permission string as used by /v2 routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    scopes = permission_string.split("|")
    for scope in scopes:
        perm_letter, groups_as_str = scope.split(" ")
        groups = groups_as_str.split(",")
        kwargs[perm_letter] = groups
    return PermissionScope.from_dict(kwargs, dsp_client)


def create_scope_from_admin_route_object(
    admin_route_object: list[dict[str, Any]], dsp_client: DspClient
) -> PermissionScope:
    """Deserializes an object returned by /admin/permissions routes to a PermissionScope object."""
    kwargs: dict[str, list[str]] = {}
    for obj in admin_route_object:
        attr_name: str = obj["name"]
        if attr_name in kwargs:
            kwargs[attr_name].append(obj["additionalInformation"])
        else:
            kwargs[attr_name] = [obj["additionalInformation"]]
    return PermissionScope.from_dict(kwargs, dsp_client)


def create_admin_route_object_from_scope(
    perm_scope: PermissionScope, dsp_client: DspClient
) -> list[dict[str, str | None]]:
    """
    Serializes a permission scope to an object that can be used for requests to /admin/permissions routes.
    Note: This route doesn't accept relative IRIs.
    """
    scope_elements: list[dict[str, str | None]] = []
    for perm_letter in perm_scope.model_fields:
        groups = perm_scope.get(perm_letter)
        for group in groups:
            full_iri = group.full_iri() if isinstance(group, BuiltinGroup) else group.full_iri(dsp_client)
            scope_elements.append(
                {
                    "additionalInformation": full_iri,
                    "name": perm_letter,
                    "permissionCode": None,
                }
            )
    return scope_elements
