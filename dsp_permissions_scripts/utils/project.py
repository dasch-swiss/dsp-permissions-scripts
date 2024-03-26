from urllib.parse import quote_plus

from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import dereference_prefix

logger = get_logger(__name__)


def _get_onto_iris_of_project(project_iri: str, dsp_client: DspClient) -> list[str]:
    try:
        response = dsp_client.get("/v2/ontologies/metadata")
    except ApiError as err:
        err.message = f"Could not get onto IRIs of project {project_iri}"
        raise err from None
    all_ontologies = response["@graph"]
    project_onto_iris = [o["@id"] for o in all_ontologies if o["knora-api:attachedToProject"]["@id"] == project_iri]
    return project_onto_iris


def _get_class_iris_of_onto(onto_iri: str, dsp_client: DspClient) -> list[str]:
    try:
        response = dsp_client.get(f"/v2/ontologies/allentities/{quote_plus(onto_iri)}")
    except ApiError as err:
        err.message = f"Could not get class IRIs of onto {onto_iri}"
        raise err from None
    all_entities = response["@graph"]
    context = response["@context"]
    class_ids = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    class_iris = [dereference_prefix(class_id, context) for class_id in class_ids]
    return class_iris


def get_all_resource_class_iris_of_project(project_iri: str, dsp_client: DspClient) -> list[str]:
    project_onto_iris = _get_onto_iris_of_project(project_iri, dsp_client)
    all_class_iris = []
    for onto_iri in project_onto_iris:
        class_iris = _get_class_iris_of_onto(onto_iri, dsp_client)
        all_class_iris.extend(class_iris)
        logger.info(f"Found {len(class_iris)} resource classes in onto {onto_iri}.")
    return all_class_iris


def get_project_iri_by_shortcode(shortcode: str, dsp_client: DspClient) -> str:
    try:
        response = dsp_client.get(f"/admin/projects/shortcode/{shortcode}")
    except ApiError as err:
        err.message = f"Could not get project IRI by shortcode {shortcode}"
        raise err from None
    iri: str = response["project"]["id"]
    return iri
