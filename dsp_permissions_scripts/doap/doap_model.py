from __future__ import annotations

from typing import Protocol
from typing import Self

from pydantic import BaseModel
from pydantic import model_validator

from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    target: DoapTarget
    scope: PermissionScope
    doap_iri: str


class DoapTarget(Protocol):
    """
    A DOAP can be defined for either a Group, or for a ResourceClass, or for a Property,
    or for a combination of ResourceClass and Property.
    In order to simplify these constraints, classes can implement this protocol.
    """

    project_iri: str


class GroupDoapTarget(BaseModel):
    project_iri: str
    group: Group


class EntityDoapTarget(BaseModel):
    project_iri: str
    resource_class: str | None = None
    property: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resource_class is None and self.property is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self


class NewDoapTarget(BaseModel):
    """Represents the target of a DOAP that is yet to be created."""

    group: Group | None = None
    resource_class: str | None = None
    property: str | None = None

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
