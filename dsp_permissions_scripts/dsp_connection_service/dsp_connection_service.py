from typing import Any, Protocol

from dsp_permissions_scripts.models.doap import Doap
from dsp_permissions_scripts.models.oap import Oap
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.models.value import ValueUpdate


class DspConnectionService(Protocol):
    def get_token(self, host: str, email: str, pw: str) -> str: 
        """requests an access token from the API, provided host, email and password."""

    def get_all_doaps_of_project(
        self,
        project_iri: str,
        host: str,
        token: str,
    ) -> list[Doap]:
        """Returns all DOAPs of the given project."""

    def update_doap_scope(
        self,
        doap_iri: str,
        scope: PermissionScope,
        host: str,
        token: str,
    ) -> Doap:
        """Updates the scope of the given DOAP."""

    def get_resource(
        self,
        resource_iri: str,
        host: str,
        token: str,
    ) -> dict[str, Any]:
        """Requests the resource with the given IRI from the API."""

    def _update_permissions_for_value(
        self,
        resource_iri: str,
        value: ValueUpdate,
        resource_type: str,
        context: dict[str, str],
        scope: PermissionScope,
        host: str,
        token: str,
    ) -> None:
        """Updates the permissions for the given value."""

    def _update_permissions_for_resource(
        self,
        resource_iri: str,
        lmd: str | None,
        resource_type: str,
        context: dict[str, str],
        scope: PermissionScope,
        host: str,
        token: str,
    ) -> None:
        """Updates the permissions for the given resource."""

    def get_all_resource_oaps_of_project(
        self,
        shortcode: str,
        host: str,
        token: str,
    ) -> list[Oap]:
        ...
