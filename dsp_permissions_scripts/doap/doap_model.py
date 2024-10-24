from __future__ import annotations

import re
from typing import Self

from pydantic import BaseModel
from pydantic import model_validator

from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    target: GroupDoapTarget | EntityDoapTarget
    scope: PermissionScope
    doap_iri: str


class GroupDoapTarget(BaseModel):
    project_iri: str
    group: Group


class EntityDoapTarget(BaseModel):
    """
    Note that the resclass IRIs and property IRIs are in the environment-agnostic format
    "http://www.knora.org/ontology/<shortcode>/<ontoname>#<classname_or_property_name>"
    """

    project_iri: str
    resclass_iri: str | None = None
    property_iri: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resclass_iri is None and self.property_iri is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self

    @model_validator(mode="after")
    def _validate_iri_format(self) -> Self:
        rgx = r"http://www\.knora\.org/ontology/[A-Fa-f0-9]{4}/[^/#]+#[^/#]+"
        iri_format = "http://www.knora.org/ontology/<shortcode>/<ontoname>#<classname_or_property_name>"
        if self.resclass_iri and not re.search(rgx, self.resclass_iri):
            raise ValueError(f"The IRI must be in the format '{iri_format}', but you provided {self.resclass_iri}")
        if self.property_iri and not re.search(rgx, self.property_iri):
            raise ValueError(f"The IRI must be in the format '{iri_format}', but you provided {self.property_iri}")
        return self


class NewGroupDoapTarget(BaseModel):
    """Represents the target of a DOAP that is yet to be created."""

    group: Group


class NewEntityDoapTarget(BaseModel):
    """Represents the target of a DOAP that is yet to be created."""

    resclass_name: str | None = None
    property_name: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resclass_name is None and self.property_name is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self

    @model_validator(mode="after")
    def _validate_name_format(self) -> Self:
        if self.resclass_name and any([x in self.resclass_name for x in ["#", "/", "knora.org", "dasch.swiss"]]):
            raise ValueError(f"The resource class name must not be a full IRI, but you provided {self.resclass_name}")
        if self.property_name and any([x in self.property_name for x in ["#", "/", "knora.org", "dasch.swiss"]]):
            raise ValueError(f"The property name must not be a full IRI, but you provided {self.property_name}")
        return self
