from __future__ import annotations

import re
from typing import Self

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import EmptyDoapTargetError
from dsp_permissions_scripts.models.errors import InvalidEntityDoapTargetError
from dsp_permissions_scripts.models.errors import InvalidPrefixedPropError
from dsp_permissions_scripts.models.errors import InvalidPrefixedResclassError
from dsp_permissions_scripts.models.group import PREFIXED_IRI_REGEX
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
    resclass_iri: str | None = None
    property_iri: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.resclass_iri is None and self.property_iri is None:
            raise EmptyDoapTargetError
        return self

    @model_validator(mode="after")
    def _validate_iri_format(self) -> Self:
        regexes = [
            r"^http://0.0.0.0:3333/ontology/[A-Fa-f0-9]{4}/[^/#]+/v2#[^/#]+$",
            r"^http://api\.(.+\.)?dasch\.swiss/ontology/[A-Fa-f0-9]{4}/[^/#]+/v2#[^/#]+$",
            r"^http://api\.knora\.org/ontology/knora-api/v2#[^/#]+$",
            # Response from API is sometimes in internal representation.
            # Canceled bug ticket (won't fix): https://linear.app/dasch/issue/DEV-4341
            r"^http://www.knora.org/ontology/[A-Fa-f0-9]{4}/[^/#]+#[^/#]+$",
            r"^http://www.knora.org/ontology/knora-base#[^/#]+$",
        ]
        if self.resclass_iri and not any(re.search(r, self.resclass_iri) for r in regexes):
            raise InvalidEntityDoapTargetError(self.resclass_iri)
        if self.property_iri and not any(re.search(r, self.property_iri) for r in regexes):
            raise InvalidEntityDoapTargetError(self.property_iri)
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

    prefixed_class: str | None = None
    prefixed_prop: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.prefixed_class is None and self.prefixed_prop is None:
            raise EmptyDoapTargetError
        return self

    @model_validator(mode="after")
    def _validate_name_format(self) -> Self:
        def _fails(s: str) -> bool:
            contains_forbidden = any(x in s for x in ["#", "/", "knora.org", "dasch.swiss"])
            fails_regex = not re.search(PREFIXED_IRI_REGEX, s)
            return contains_forbidden or fails_regex

        if self.prefixed_class and _fails(self.prefixed_class):
            raise InvalidPrefixedResclassError(self.prefixed_class)
        if self.prefixed_prop and _fails(self.prefixed_prop):
            raise InvalidPrefixedPropError(self.prefixed_prop)
        return self
