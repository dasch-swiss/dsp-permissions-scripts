from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import dereference_prefix

logger = get_logger(__name__)


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


def get_all_resource_class_iris_of_project(
    onto_iris: list[str], dsp_client: DspClient, oap_config: OapRetrieveConfig
) -> list[str]:
    all_class_iris = []
    for onto_iri in onto_iris:
        class_iris = _get_class_iris_of_onto(onto_iri, dsp_client)
        all_class_iris.extend(class_iris)
        logger.info(f"Found {len(class_iris)} resource classes in onto {onto_iri}.")
    if oap_config.retrieve_resources == "specified_res_classes":
        all_class_iris = [x for x in all_class_iris if x in oap_config.specified_res_classes]
    return all_class_iris


def get_project_iri_and_onto_iris_by_shortcode(shortcode: str, dsp_client: DspClient) -> tuple[str, list[str]]:
    try:
        response = dsp_client.get(f"/admin/projects/shortcode/{shortcode}")
    except ApiError as err:
        err.message = f"Could not get project IRI by shortcode {shortcode}"
        raise err from None
    project_iri: str = response["project"]["id"]
    onto_iris: list[str] = response["project"]["ontologies"]
    return project_iri, onto_iris
