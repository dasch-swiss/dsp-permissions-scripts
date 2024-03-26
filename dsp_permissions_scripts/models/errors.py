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
