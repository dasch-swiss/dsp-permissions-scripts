from typing import Any
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.doap import Doap, create_doap_from_admin_route_response
from dsp_permissions_scripts.models.oap import Oap
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.models.value import ValueUpdate


def _get_protocol(host: str) -> str:
    return "http" if host.startswith("localhost") else "https"


class DspConnectionServiceLive:
    def get_token(self, host: str, email: str, pw: str) -> str: 
        """requests an access token from the API, provided host, email and password."""
        protocol = _get_protocol(host)
        url = f"{protocol}://{host}/v2/authentication"
        response = requests.post(url, json={"email": email, "password": pw}, timeout=5)
        assert response.status_code == 200
        token: str = response.json()["token"]
        return token

    def get_all_doaps_of_project(
        self,
        project_iri: str,
        host: str,
        token: str,
    ) -> list[Doap]:
        """Returns all DOAPs of the given project."""
        headers = {"Authorization": f"Bearer {token}"}
        project_iri = quote_plus(project_iri, safe="")
        protocol = _get_protocol(host)
        url = f"{protocol}://{host}/admin/permissions/doap/{project_iri}"
        response = requests.get(url, headers=headers, timeout=5)
        assert response.status_code == 200
        doaps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
        doap_objects = [create_doap_from_admin_route_response(doap) for doap in doaps]
        return doap_objects

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
