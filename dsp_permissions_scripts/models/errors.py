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
class OapRetrieveConfigEmptyError(Exception):
    message: str = "retrieve_resources cannot be False if retrieve_values is 'none'"


@dataclass
class OapEmptyError(Exception):
    message: str = "An OAP must specify at least one resource_oap or one value_oap"
