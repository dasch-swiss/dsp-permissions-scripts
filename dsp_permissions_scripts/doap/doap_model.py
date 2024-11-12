from __future__ import annotations

from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    model_config = ConfigDict(extra="forbid")

    target: GroupDoapTarget | EntityDoapTarget
    scope: PermissionScope
    doap_iri: str


class GroupDoapTarget(BaseModel):
    """The group for which a DOAP is defined"""

    model_config = ConfigDict(extra="forbid")

    project_iri: str
    group: Group


class EntityDoapTarget(BaseModel):
    """The resource class and/or property for which a DOAP is defined"""

    model_config = ConfigDict(extra="forbid")

    project_iri: str
    resource_class: str | None = None
    property: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resource_class is None and self.property is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self


class NewGroupDoapTarget(BaseModel):
    """
    The group for which a DOAP is defined, if the DOAP is yet to be created.
    At this stage, the project IRI is not known yet.
    """

    model_config = ConfigDict(extra="forbid")

    group: Group


class NewEntityDoapTarget(BaseModel):
    """
    The resource class and/or property for which a DOAP is defined, if the DOAP is yet to be created.
    At this stage, neither the project IRI nor the full IRIs of the class/prop are known yet.
    So the class/prop must be defined by their prefixed name (onto:name).
    """

    model_config = ConfigDict(extra="forbid")

    resource_class: str | None = None
    property: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resource_class is None and self.property is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self
