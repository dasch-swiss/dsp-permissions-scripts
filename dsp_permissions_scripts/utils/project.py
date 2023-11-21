from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import dereference_prefix
from dsp_permissions_scripts.utils.try_request import http_call_with_retry

logger = get_logger(__name__)


def _get_onto_iris_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/ontologies/metadata"
    headers = {"Authorization": f"Bearer {token}"}
    response = http_call_with_retry(
        action=lambda: requests.get(url, headers=headers, timeout=20),
        err_msg="Could not get onto IRIs",
    )
    if response.status_code != 200:
        raise ApiError("Could not get onto IRIs", response.text, response.status_code)
    all_ontologies = response.json().get("@graph")
    project_onto_iris = [o["@id"] for o in all_ontologies if o["knora-api:attachedToProject"]["@id"] == project_iri]
    return project_onto_iris


def _get_class_iris_of_onto(
    host: str,
    onto_iri: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/ontologies/allentities/{quote_plus(onto_iri)}"
    headers = {"Authorization": f"Bearer {token}"}
    response = http_call_with_retry(
        action=lambda: requests.get(url, headers=headers, timeout=20),
        err_msg="Could not get class IRIs",
    )
    if response.status_code != 200:
        raise ApiError("Could not get class IRIs", response.text, response.status_code)
    all_entities = response.json()["@graph"]
    context = response.json()["@context"]
    class_ids = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    class_iris = [dereference_prefix(class_id, context) for class_id in class_ids]
    return class_iris


def get_all_resource_class_iris_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[str]:
    logger.info(f"Getting all resource class IRIs of project {project_iri}...")
    project_onto_iris = _get_onto_iris_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    all_class_iris = []
    for onto_iri in project_onto_iris:
        class_iris = _get_class_iris_of_onto(
            host=host,
            onto_iri=onto_iri,
            token=token,
        )
        all_class_iris.extend(class_iris)
        logger.info(f"Found {len(class_iris)} resource classes in onto {onto_iri}.")
    return all_class_iris


def get_project_iri_by_shortcode(shortcode: str, host: str) -> str:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/projects/shortcode/{shortcode}"
    response = http_call_with_retry(
        action=lambda: requests.get(url, timeout=20),
        err_msg="Cannot retrieve project IRI",
    )
    if response.status_code != 200:
        raise ApiError("Cannot retrieve project IRI", response.text, response.status_code)
    iri: str = response.json()["project"]["id"]
    return iri
