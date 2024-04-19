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
class SpecifiedPropsEmptyError(ValueError):
    message: str = "specified_props must not be empty if retrieve_values is 'specified_props'"


@dataclass
class SpecifiedPropsNotEmptyError(ValueError):
    message: str = "specified_props must be empty if retrieve_values is not 'specified_props'"


@dataclass
class OapRetrieveConfigEmptyError(ValueError):
    message: str = "retrieve_resources cannot be False if retrieve_values is 'none'"


@dataclass
class EmptyScopeError(Exception):
    message: str = "PermissionScope must not be empty"
