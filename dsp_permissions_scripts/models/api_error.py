from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApiError(Exception):
    """Exception raised when an error occurs while calling DSP-API."""

    message: str
    response_text: str | None = None
    status_code: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
