from __future__ import annotations

from typing import Self

from pydantic import BaseModel
from pydantic import model_validator

from dsp_permissions_scripts.models.group import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    target: GroupDoapTarget | EntityDoapTarget
    scope: PermissionScope
    doap_iri: str


class GroupDoapTarget(BaseModel):
    project_iri: str
    group: BuiltinGroup


class EntityDoapTarget(BaseModel):
    project_iri: str
    resource_class: str | None = None
    property: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resource_class is None and self.property is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self


class NewGroupDoapTarget(BaseModel):
    """Represents the target of a DOAP that is yet to be created."""

    group: BuiltinGroup


class NewEntityDoapTarget(BaseModel):
    """Represents the target of a DOAP that is yet to be created."""

    resource_class: str | None = None
    property: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resource_class is None and self.property is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self
