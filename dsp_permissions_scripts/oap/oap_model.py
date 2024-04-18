from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from dsp_permissions_scripts.models.errors import OapEmptyError
from dsp_permissions_scripts.models.errors import OapRetrieveConfigEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedPropsEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedPropsNotEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedResClassesEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedResClassesNotEmptyError
from dsp_permissions_scripts.models.scope import PermissionScope


class Oap(BaseModel):
    """
    Model representing an object access permission of a resource and its values.
    If only the resource is of interest, value_oaps will be an empty list.
    If only the values (or a part of them) are of interest, resource_oap will be None.
    """

    resource_oap: ResourceOap | None
    value_oaps: list[ValueOap]

    @model_validator(mode="after")
    def check_consistency(self) -> Oap:
        if not self.resource_oap and not self.value_oaps:
            raise OapEmptyError()
        return self


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

    retrieve_resources: Literal["all", "specified_res_classes", "none"] = "none"
    specified_res_classes: list[str] = []
    retrieve_values: Literal["all", "specified_props", "none"] = "none"
    specified_props: list[str] = []
    context: dict[str, str] = {}

    @model_validator(mode="after")
    def check_specified_res_classes(self) -> OapRetrieveConfig:
        if self.retrieve_resources == "specified_res_classes" and not self.specified_res_classes:
            raise SpecifiedResClassesEmptyError()
        if self.retrieve_resources != "specified_res_classes" and self.specified_res_classes:
            raise SpecifiedResClassesNotEmptyError()
        return self

    @model_validator(mode="after")
    def check_specified_props(self) -> OapRetrieveConfig:
        if self.retrieve_values == "specified_props" and not self.specified_props:
            raise SpecifiedPropsEmptyError()
        if self.retrieve_values != "specified_props" and self.specified_props:
            raise SpecifiedPropsNotEmptyError()
        return self

    @model_validator(mode="after")
    def check_config_empty(self) -> OapRetrieveConfig:
        if self.retrieve_resources == "none" and self.retrieve_values == "none":
            raise OapRetrieveConfigEmptyError()
        return self
