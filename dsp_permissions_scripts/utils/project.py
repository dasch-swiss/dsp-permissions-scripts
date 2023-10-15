import warnings
from typing import Iterable
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp
from dsp_permissions_scripts.utils.helpers import dereference_prefix
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string

logger = get_logger(__name__)


def _get_all_resource_class_iris_of_project(
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


def _get_onto_iris_of_project(
    project_iri: str,
    host: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/ontologies/metadata"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
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
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code != 200:
        raise ApiError("Could not get class IRIs", response.text, response.status_code)
    all_entities = response.json()["@graph"]
    context = response.json()["@context"]
    class_ids = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    class_iris = [dereference_prefix(class_id, context) for class_id in class_ids]
    return class_iris


def _get_all_resource_oaps_of_resclass(
    host: str,
    resclass_iri: str,
    project_iri: str,
    token: str,
) -> list[Oap]:
    print(f"{get_timestamp()}: Getting all resource OAPs of class {resclass_iri}...")
    logger.info(f"Getting all resource OAPs of class {resclass_iri}...")
    protocol = get_protocol(host)
    headers = {"X-Knora-Accept-Project": project_iri, "Authorization": f"Bearer {token}"}
    resources: list[Oap] = []
    page = 0
    more = True
    while more:
        logger.info(f"Getting page {page}...")
        try:
            more, iris = _get_next_page(
                protocol=protocol,
                host=host,
                resclass_iri=resclass_iri,
                page=page,
                headers=headers,
            )
            resources.extend(iris)
            page += 1
        except ApiError as err:
            logger.error(f"{err}\nStop getting more pages, return what has been retrieved so far.")
            warnings.warn(f"{err.message}\nStop getting more pages, return what has been retrieved so far.")
            more = False
    print(f"{get_timestamp()}: Retrieved {len(resources)} resource OAPs of class {resclass_iri}.")
    logger.info(f"Retrieved {len(resources)} resource OAPs of class {resclass_iri}.")
    return resources


def _get_next_page(
    protocol: str,
    host: str,
    resclass_iri: str,
    page: int,
    headers: dict[str, str],
) -> tuple[bool, list[Oap]]:
    """
    Get the resource IRIs of a resource class, one page at a time.
    DSP-API returns results page-wise:
    a list of 25 resources if there are 25 resources or more,
    a list of less than 25 resources if there are less than 25 remaining,
    1 resource (not packed in a list) if there is only 1 remaining,
    and an empty response content with status code 200 if there are no resources remaining.
    This means that the page must be incremented until the response contains 0 or 1 resource.
    """
    url = f"{protocol}://{host}/v2/resources?resourceClass={quote_plus(resclass_iri)}&page={page}"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code != 200:
        raise ApiError("Could not get next page", response.text, response.status_code)
    result = response.json()
    if "@graph" in result:
        # result contains several resources: return them, then continue with next page
        oaps = []
        for r in result["@graph"]:
            scope = create_scope_from_string(r["knora-api:hasPermissions"])
            oaps.append(Oap(scope=scope, object_iri=r["@id"]))
        return True, oaps
    elif "@id" in result:
        # result contains only 1 resource: return it, then stop (there will be no more resources)
        scope = create_scope_from_string(result["knora-api:hasPermissions"])
        return False, [Oap(scope=scope, object_iri=result["@id"])]
    else:
        # there are no more resources
        return False, []


def get_project_iri_by_shortcode(shortcode: str, host: str) -> str:
    """
    Retrieves the IRI of a project by its shortcode.
    """
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/projects/shortcode/{shortcode}"
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        raise ApiError("Cannot retrieve project IRI", response.text, response.status_code)
    iri: str = response.json()["project"]["id"]
    return iri


def get_all_resource_oaps_of_project(
    shortcode: str,
    host: str,
    token: str,
    excluded_class_iris: Iterable[str] = (),
) -> list[Oap]:
    logger.info(f"******* Getting all resource OAPs of project {shortcode} *******")
    print(f"{get_timestamp()}: ******* Getting all resource OAPs of project {shortcode} *******")
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    all_resource_oaps = []
    resclass_iris = _get_all_resource_class_iris_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    resclass_iris = [x for x in resclass_iris if x not in excluded_class_iris]
    for resclass_iri in resclass_iris:
        resource_oaps = _get_all_resource_oaps_of_resclass(
            host=host,
            resclass_iri=resclass_iri,
            project_iri=project_iri,
            token=token,
        )
        all_resource_oaps.extend(resource_oaps)
    logger.info(f"Retrieved a TOTAL of {len(all_resource_oaps)} resource OAPs of project {shortcode}.")
    print(f"{get_timestamp()}: Retrieved a TOTAL of {len(all_resource_oaps)} resource OAPs of project {shortcode}.")
    return all_resource_oaps
