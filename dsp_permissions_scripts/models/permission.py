from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, field_validator, model_validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScopeElement(BaseModel):
    group_iri: str | BuiltinGroup
    permission_code: str

    @field_validator("permission_code")
    @classmethod
    def name_must_represent_permission(cls, v: str) -> str:
        assert v in {"RV", "V", "M", "D", "CR"}
        return v


class PermissionScope:
    restricted_view: list[str | BuiltinGroup] | None = []
    view: list[str | BuiltinGroup] | None = []
    modify: list[str | BuiltinGroup] | None = []
    delete: list[str | BuiltinGroup] | None = []
    change_rights: list[str | BuiltinGroup] | None = []

    def __init__(self, permission_string: str) -> None:
        scopes = permission_string.split("|")
        for scope in scopes:
            perm_letter, groups_as_str = scope.split(" ")
            groups = groups_as_str.split(",")
            groups = [g.replace("knora-admin:", "http://www.knora.org/ontology/knora-admin#") for g in groups]
            match perm_letter:
                case "RV":
                    self.restricted_view = list(groups)
                case "V":
                    self.view = list(groups)
                case "M":
                    self.modify = list(groups)
                case "D":
                    self.delete = list(groups)
                case "CR":
                    self.change_rights = list(groups)
                case _:
                    raise ValueError(f"Invalid permission letter {perm_letter}")

    def as_admin_route_object(self) -> list[dict[str, Any]]:
        """Serializes a permission scope to a shape that can be used for requests to /admin/permissions routes."""
        scope_elements = []
        for letter, groups in [
            ("RV", self.restricted_view), 
            ("V", self.view), 
            ("M", self.modify), 
            ("D", self.delete), 
            ("CR", self.change_rights)
        ]:
            if groups:
                scope_elements.append(
                    {
                        "additionalInformation": groups,
                        "name": letter,
                        "permissionCode": None,
                    }
                )
        return scope_elements
    
    def as_permission_string(self) -> str:
        """Serializes a permission scope to a permissions string as used by /v2 routes."""
        as_dict = {}
        for letter, groups in [
            ("RV", self.restricted_view), 
            ("V", self.view), 
            ("M", self.modify), 
            ("D", self.delete), 
            ("CR", self.change_rights)
        ]:
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
    scope: list[PermissionScopeElement]
    iri: str


class DoapTargetType(Enum):
    ALL = "all"
    GROUP = "group"
    RESOURCE_CLASS = "resource_class"
    PROPERTY = "property"
