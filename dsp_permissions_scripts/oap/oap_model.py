from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.scope import PermissionScope


class Oap(BaseModel):
    """
    Model representing an object access permission of a resource and its values.
    If only the resource is of interest, value_oaps will be an empty list.
    If only the values (or a part of them) are of interest, resource_oap will be None.
    """

    resource_oap: ResourceOap | None
    value_oaps: list[ValueOap]


class ResourceOap(BaseModel):
    """Model representing an object access permission of a resource"""

    scope: PermissionScope
    resource_iri: str


class ValueOap(BaseModel):
    """
    Model representing an object access permission of a value.

    Fields:
    scope: permissions of this value
    value_iri: IRI of the value
    property: property whith which the value relates to its resource
    value_type: type of the value, e.g. "knora-api:TextValue"
    """

    scope: PermissionScope
    property: str
    value_type: str
    value_iri: str
    resource_iri: str


class OapRetrieveConfig(BaseModel):

    model_config = ConfigDict(frozen=True)

    retrieve_resources: bool = True
    retrieve_values: Literal["all", "specified_props", "none"] = "none"
    specified_props: list[str] = []

    @model_validator(mode="after")
    def check_consistency(self) -> OapRetrieveConfig:
        if self.retrieve_values == "specified_props" and not self.specified_props:
            raise ValueError("specified_props must not be empty if retrieve_values is 'specified_props'")
        if self.retrieve_values != "specified_props" and self.specified_props:
            raise ValueError("specified_props must be empty if retrieve_values is not 'specified_props'")
        return self
