from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _get_class_localnames_of_onto_and_context(onto_iri: str, dsp_client: DspClient) -> tuple[list[str], dict[str, str]]:
    try:
        response = dsp_client.get(f"/v2/ontologies/allentities/{quote_plus(onto_iri)}")
    except ApiError as err:
        err.message = f"Could not get class IRIs of onto {onto_iri}"
        raise err from None
    all_entities = response["@graph"]
    context = response["@context"]
    class_localnames = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    return class_localnames, context


def get_all_resource_class_localnames_of_project(
    onto_iris: list[str], dsp_client: DspClient, oap_config: OapRetrieveConfig
) -> list[str]:
    all_class_localnames: list[str] = []
    for onto_iri in onto_iris:
        class_localnames, onto_context = _get_class_localnames_of_onto_and_context(onto_iri, dsp_client)
        all_class_localnames.extend(class_localnames)
        oap_config.context.update(onto_context)
        logger.info(f"Found {len(class_localnames)} resource classes in onto {onto_iri}.")
    if oap_config.retrieve_resources == "specified_res_classes":
        all_class_localnames = [x for x in all_class_localnames if x in oap_config.specified_res_classes]
    return all_class_localnames


def get_proj_iri_and_onto_iris_by_shortcode(shortcode: str, dsp_client: DspClient) -> tuple[str, list[str]]:
    try:
        response = dsp_client.get(f"/admin/projects/shortcode/{shortcode}")
    except ApiError as err:
        err.message = f"Could not get project IRI by shortcode {shortcode}"
        raise err from None
    project_iri: str = response["project"]["id"]
    onto_iris: list[str] = response["project"]["ontologies"]
    return project_iri, onto_iris
