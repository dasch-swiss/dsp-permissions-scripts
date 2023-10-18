import warnings
from typing import Any, Iterable
from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import (
    get_all_resource_class_iris_of_project,
    get_project_iri_by_shortcode,
)
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string
from dsp_permissions_scripts.utils.try_request import http_call_with_retry

logger = get_logger(__name__)


def get_resource(
    resource_iri: str,
    host: str,
    token: str,
) -> dict[str, Any]:
    """Requests the resource with the given IRI from DSP-API"""
    iri = quote_plus(resource_iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/resources/{iri}"
    headers = {"Authorization": f"Bearer {token}"}
    response = http_call_with_retry(
        action=lambda: requests.get(url, headers=headers, timeout=10),
        err_msg=f"Error while getting resource {resource_iri}",
    )
    if response.status_code != 200:
        raise ApiError( f"Error while getting resource {resource_iri}", response.text, response.status_code)
    data: dict[str, Any] = response.json()
    return data


def _get_all_resource_oaps_of_resclass(
    host: str,
    resclass_iri: str,
    project_iri: str,
    token: str,
) -> list[Oap]:
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
    print(f"Retrieved {len(resources)} resource OAPs of class {resclass_iri}")
    logger.info(f"Retrieved {len(resources)} resource OAPs of class {resclass_iri}")
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
    response = http_call_with_retry(
        action=lambda: requests.get(url, headers=headers, timeout=20),
        err_msg="Could not get next page",
    )
    if response.status_code != 200:
        raise ApiError("Could not get next page", response.text, response.status_code)
    result = response.json()

    # result contains several resources: return them, then continue with next page
    if "@graph" in result:
        oaps = []
        for r in result["@graph"]:
            scope = create_scope_from_string(r["knora-api:hasPermissions"])
            oaps.append(Oap(scope=scope, object_iri=r["@id"]))
        return True, oaps
    
    # result contains only 1 resource: return it, then stop (there will be no more resources)
    if "@id" in result:
        scope = create_scope_from_string(result["knora-api:hasPermissions"])
        return False, [Oap(scope=scope, object_iri=result["@id"])]

    # there are no more resources
    return False, []



def get_all_resource_oaps_of_project(
    shortcode: str,
    host: str,
    token: str,
    excluded_class_iris: Iterable[str] = (),
) -> list[Oap]:
    logger.info(f"******* Getting all resource OAPs of project {shortcode} *******")
    print(f"******* Getting all resource OAPs of project {shortcode} *******")
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    all_resource_oaps = []
    resclass_iris = get_all_resource_class_iris_of_project(
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
    print(f"Retrieved a TOTAL of {len(all_resource_oaps)} resource OAPs of project {shortcode}.")
    return all_resource_oaps
