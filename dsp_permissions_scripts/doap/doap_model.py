from __future__ import annotations

import re
from typing import Self

from pydantic import BaseModel
from pydantic import model_validator

from dsp_permissions_scripts.models.group import PREFIXED_IRI_REGEX
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.models.scope import PermissionScope


class Doap(BaseModel):
    """Model representing a DOAP, containing the target, the scope and the IRI of the DOAP."""

    target: GroupDoapTarget | EntityDoapTarget
    scope: PermissionScope
    doap_iri: str


class GroupDoapTarget(BaseModel):
    """The group for which a DOAP is defined"""

    project_iri: str
    group: Group


class EntityDoapTarget(BaseModel):
    """The resource class and/or property for which a DOAP is defined"""

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
        regexes = [
            r"^http://0.0.0.0:3333/ontology/[A-Fa-f0-9]{4}/[^/#]+/v2#[^/#]+$",
            r"^http://api\.(.+\.)?dasch\.swiss/ontology/[A-Fa-f0-9]{4}/[^/#]+/v2#[^/#]+$",
            r"^http://api\.knora\.org/ontology/knora-api/v2#[^/#]+$",
        ]
        iri_formats = [
            "http://0.0.0.0:3333/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>",
            "http://api.<subdomain>.dasch.swiss/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>",
            "http://api.knora.org/ontology/knora-api/v2#<knora_base_class_or_base_property>",
        ]
        if self.resclass_iri and not any(re.search(r, self.resclass_iri) for r in regexes):
            raise ValueError(
                f"The IRI must be in one of the formats {iri_formats}, but you provided {self.resclass_iri}"
            )
        if self.property_iri and not any(re.search(r, self.property_iri) for r in regexes):
            raise ValueError(
                f"The IRI must be in one of the formats {iri_formats}, but you provided {self.property_iri}"
            )
        return self


class NewGroupDoapTarget(BaseModel):
    """
    The group for which a DOAP is defined, if th DOAP is yet to be created.
    At this stage, the project IRI is not known yet.
    """

    group: Group


class NewEntityDoapTarget(BaseModel):
    """
    The resource class and/or property for which a DOAP is defined, if the DOAP is yet to be created.
    At this stage, neither the project IRI nor the full IRIs of the class/prop are known yet.
    So the class/prop must be defined by their prefixed name (onto:name).
    """

    prefixed_class: str | None = None
    prefixed_prop: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.prefixed_class is None and self.prefixed_prop is None:
            raise ValueError("At least one of resource_class or property must be set")
        return self

    @model_validator(mode="after")
    def _validate_name_format(self) -> Self:
        if self.prefixed_class and any([x in self.prefixed_class for x in ["#", "/", "knora.org", "dasch.swiss"]]):
            raise ValueError(f"The resource class name must not be a full IRI, but you provided {self.prefixed_class}")
        if self.prefixed_class and not re.search(PREFIXED_IRI_REGEX, self.prefixed_class):
            raise ValueError(
                "The resource class name must be in the format 'onto:resclass_name', "
                f"but you provided {self.prefixed_class}"
            )
        if self.prefixed_prop and any([x in self.prefixed_prop for x in ["#", "/", "knora.org", "dasch.swiss"]]):
            raise ValueError(f"The property name must not be a full IRI, but you provided {self.prefixed_prop}")
        if self.prefixed_prop and not re.search(PREFIXED_IRI_REGEX, self.prefixed_prop):
            msg = f"The property name must be in the format 'onto:resclass_name', but you provided {self.prefixed_prop}"
            raise ValueError(msg)
        return self
