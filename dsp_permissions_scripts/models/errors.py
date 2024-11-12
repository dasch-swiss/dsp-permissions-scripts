import pprint
from dataclasses import dataclass


@dataclass
class ApiError(Exception):
    """Exception raised when an error occurs while calling DSP-API."""

    message: str
    response_text: str | None = None
    status_code: int | None = None

    def __str__(self) -> str:
        return pprint.pformat(vars(self))


@dataclass
class PermissionsAlreadyUpToDate(Exception):
    message: str = "The submitted permissions are the same as the current ones"


@dataclass
class SpecifiedResClassesEmptyError(Exception):
    message: str = "specified_res_classes must not be empty if retrieve_resources is 'specified_res_classes'"


@dataclass
class SpecifiedResClassesNotEmptyError(Exception):
    message: str = "specified_res_classes must be empty if retrieve_resources is not 'specified_res_classes'"


@dataclass
class SpecifiedPropsEmptyError(Exception):
    message: str = "specified_props must not be empty if retrieve_values is 'specified_props'"


@dataclass
class SpecifiedPropsNotEmptyError(Exception):
    message: str = "specified_props must be empty if retrieve_values is not 'specified_props'"


@dataclass
class EmptyScopeError(Exception):
    message: str = "PermissionScope must not be empty"


@dataclass
class InvalidGroupError(Exception):
    message: str


@dataclass
class InvalidIRIError(Exception):
    message: str


@dataclass
class EmptyDoapTargetError(Exception):
    message = "At least one of resource_class or property must be set"


class InvalidEntityDoapTargetError(Exception):
    message: str

    def __init__(self, resclass_iri: str) -> None:
        iri_formats = [
            "http://0.0.0.0:3333/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>",
            "http://api.<subdomain>.dasch.swiss/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>",
            "http://api.knora.org/ontology/knora-api/v2#<knora_base_class_or_base_property>",
        ]
        self.message = f"The IRI must be in one of the formats {iri_formats}, but you provided {resclass_iri}"
