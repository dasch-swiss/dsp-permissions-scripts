from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, model_validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScopeFields(Enum):
    CR = "change_rights"
    D = "delete"
    M = "modify"
    V = "view"
    RV = "restricted_view"


class PermissionScope(BaseModel):
    change_rights: list[str | BuiltinGroup] | None = []
    delete: list[str | BuiltinGroup] | None = []
    modify: list[str | BuiltinGroup] | None = []
    view: list[str | BuiltinGroup] | None = []
    restricted_view: list[str | BuiltinGroup] | None = []

    @classmethod
    def create_from_string(cls, permission_string: str) -> Self:
        kwargs = {}
        scopes = permission_string.split("|")
        for scope in scopes:
            perm_letter, groups_as_str = scope.split(" ")
            attr_name = PermissionScopeFields[perm_letter].value
            groups = groups_as_str.split(",")
            groups = [g.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#") for g in groups]
            kwargs[attr_name] = groups
        return cls(**kwargs)
    
    @classmethod
    def create_from_admin_route_object(cls, admin_route_object: list[dict[str, Any]]) -> Self:
        kwargs = {}
        for obj in admin_route_object:
            attr_name = PermissionScopeFields[obj["name"]].value
            groups_full = obj["additionalInformation"]
            groups = [
                g.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:") for g in groups_full
            ]
            kwargs[attr_name] = groups
        return cls(**kwargs)

    def as_admin_route_object(self) -> list[dict[str, Any]]:
        """Serializes a permission scope to a shape that can be used for requests to /admin/permissions routes."""
        scope_elements = []
        for f in PermissionScopeFields:
            letter = f.name
            groups = getattr(self, f.value)
            if groups:
                groups_as_str = [g.value if isinstance(g, BuiltinGroup) else g for g in groups]
                groups_as_str = [
                    g.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:") for g in groups_as_str
                ]
                scope_elements.append(
                    {
                        "additionalInformation": groups_as_str,
                        "name": letter,
                        "permissionCode": None,
                    }
                )
        return scope_elements
    
    def as_permission_string(self) -> str:
        """Serializes a permission scope to a permissions string as used by /v2 routes."""
        as_dict = {}
        for f in PermissionScopeFields:
            letter = f.name
            groups = getattr(self, f.value)
            if groups:
                groups_as_str = [g.value if isinstance(g, BuiltinGroup) else g for g in groups]
                as_dict[letter] = [
                    g.replace("http://www.knora.org/ontology/knora-admin#", "knora-admin:") for g in groups_as_str
                ]
        strs = [f"{k} {','.join(l)}" for k, l in as_dict.items()]
        return "|".join(strs)
                
        
class DoapTarget(BaseModel):
    project: str
    group: str | None
    resource_class: str | None
    property: str | None

    @model_validator(mode="after")
    def assert_correct_combination(self) -> Self:
        # asserts that DOAP is only defined for Group or ResourceClass or Property
        # or a combination of ResourceClass and Property
        match (self.group, self.resource_class, self.property):
            case (None, None, None):
                raise ValueError("At least one of group, resource_class or property must be set")
            case (_, None, None) | (None, _, _):
                pass
            case _:
                raise ValueError("Invalid combination of group, resource_class and property")
        return self


class Doap(BaseModel):
    """
    Model representing a DOAP, containing the target, the scope and the IRI of the DOAP.
    """

    target: DoapTarget
    scope: PermissionScope
    iri: str


class DoapTargetType(Enum):
    ALL = "all"
    GROUP = "group"
    RESOURCE_CLASS = "resource_class"
    PROPERTY = "property"
