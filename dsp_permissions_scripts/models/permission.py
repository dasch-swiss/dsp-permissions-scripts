from enum import Enum
from typing import Self

from pydantic import BaseModel, field_validator, model_validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScopeElement(BaseModel):
    info: str | BuiltinGroup
    name: str

    @field_validator("name")
    @classmethod
    def name_must_represent_permission(cls, v: str) -> str:
        assert v in {"RV", "V", "M", "D", "CR"}
        return v


class PermissionScope:
    scope_elements: dict[str, str]

    def __init__(self, scope_elements: dict[str, str] | None, permission_string: str | None) -> None:
        if bool(scope_elements) == bool(permission_string):
            raise ValueError("Either scope_elements or permission_string must be set")
        elif scope_elements:
            self.scope_elements = scope_elements
        else:
            self.scope_elements = self._parse_permission_string(permission_string)
    


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
