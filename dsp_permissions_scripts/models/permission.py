from enum import Enum
from typing import Self

from pydantic import BaseModel, model_validator

from dsp_permissions_scripts.models.scope import PermissionScope


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
