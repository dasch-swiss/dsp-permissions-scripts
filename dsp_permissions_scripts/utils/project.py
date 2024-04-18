from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _get_class_ids_of_onto(onto_iri: str, dsp_client: DspClient) -> list[str]:
    try:
        response = dsp_client.get(f"/v2/ontologies/allentities/{quote_plus(onto_iri)}")
    except ApiError as err:
        err.message = f"Could not get class IRIs of onto {onto_iri}"
        raise err from None
    all_entities = response["@graph"]
    class_ids = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    return class_ids


def get_all_resource_class_ids_of_project(
    onto_iris: list[str], dsp_client: DspClient, oap_config: OapRetrieveConfig
) -> list[str]:
    all_class_ids = []
    for onto_iri in onto_iris:
        class_ids = _get_class_ids_of_onto(onto_iri, dsp_client)
        all_class_ids.extend(class_ids)
        logger.info(f"Found {len(class_ids)} resource classes in onto {onto_iri}.")
    if oap_config.retrieve_resources == "specified_res_classes":
        all_class_ids = [x for x in all_class_ids if x in oap_config.specified_res_classes]
    return all_class_ids


def get_project_iri_and_onto_iris_by_shortcode(shortcode: str, dsp_client: DspClient) -> tuple[str, list[str]]:
    try:
        response = dsp_client.get(f"/admin/projects/shortcode/{shortcode}")
    except ApiError as err:
        err.message = f"Could not get project IRI by shortcode {shortcode}"
        raise err from None
    project_iri: str = response["project"]["id"]
    onto_iris: list[str] = response["project"]["ontologies"]
    return project_iri, onto_iris
