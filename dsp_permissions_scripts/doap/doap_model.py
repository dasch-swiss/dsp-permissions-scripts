from __future__ import annotations

from typing import Annotated
from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import Discriminator
from pydantic import Tag
from pydantic import model_validator

from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope


def discriminator(v: GroupDoapTarget | EntityDoapTarget | dict[str, Any]) -> str:
    if isinstance(v, GroupDoapTarget) or "group" in v:
        return "GroupDoapTarget"
    if isinstance(v, EntityDoapTarget) or "resource_class" in v or "property" in v:
        return "EntityDoapTarget"
    else:
        raise ValueError("Invalid dict for GroupDoapTarget or EntityDoapTarget")


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    target: Annotated[
        Annotated[GroupDoapTarget, Tag("GroupDoapTarget")] | Annotated[EntityDoapTarget, Tag("EntityDoapTarget")],
        Discriminator(discriminator, custom_error_type="inv_doap_target", custom_error_message="Invalid DoapTarget"),
    ]
    scope: PermissionScope
    doap_iri: str


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
