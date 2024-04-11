from typing import Any
from typing import Iterable
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_all_resource_class_iris_of_project
from dsp_permissions_scripts.utils.project import get_project_iri_and_onto_iris_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string

logger = get_logger(__name__)


def _get_all_oaps_of_resclass(
    resclass_iri: str, project_iri: str, dsp_client: DspClient, prefixed_prop: str | None
) -> list[Oap]:
    """
    prefixed_prop: retrieve the permissions from values of this property only,
    instead of the resource (e.g. "onto-name:propname" or "knora-api:hasStillImageFileValue")
    """
    logger.info(f"Getting all OAPs of class {resclass_iri}...")
    headers = {"X-Knora-Accept-Project": project_iri}
    all_oaps: list[Oap] = []
    page = 0
    more = True
    while more:
        logger.info(f"Getting page {page}...")
        try:
            more, oaps = _get_next_page(
                resclass_iri=resclass_iri,
                page=page,
                headers=headers,
                dsp_client=dsp_client,
                prefixed_prop=prefixed_prop,
            )
            all_oaps.extend(oaps)
            page += 1
        except ApiError as err:
            logger.error(f"{err}\nStop getting more pages, return what has been retrieved so far.")
            more = False
    logger.info(f"Retrieved {len(all_oaps)} OAPs of class {resclass_iri}")
    return all_oaps


def _get_next_page(
    resclass_iri: str,
    page: int,
    headers: dict[str, str],
    dsp_client: DspClient,
    prefixed_prop: str | None,
) -> tuple[bool, list[Oap]]:
    """
    Get the resource IRIs of a resource class, one page at a time.
    DSP-API returns results page-wise:
    a list of 25 resources if there are 25 resources or more,
    a list of less than 25 resources if there are less than 25 remaining,
    1 resource (not packed in a list) if there is only 1 remaining,
    and an empty response content with status code 200 if there are no resources remaining.
    This means that the page must be incremented until the response contains 0 or 1 resource.

    prefixed_prop: retrieve the permissions from values of this property only,
    instead of the resource (e.g. "onto-name:propname" or "knora-api:hasStillImageFileValue")
    """
    route = f"/v2/resources?resourceClass={quote_plus(resclass_iri)}&page={page}"
    try:
        result = dsp_client.get(route, headers=headers)
    except ApiError as err:
        err.message = "Could not get next page"
        raise err from None

    # result contains several resources: return them, then continue with next page
    if "@graph" in result:
        oaps: list[Oap] = []
        for r in result["@graph"]:
            oaps.extend(_get_oaps_of_one_resource(r, prefixed_prop))
        return True, oaps

    # result contains only 1 resource: return it, then stop (there will be no more resources)
    if "@id" in result:
        oaps = _get_oaps_of_one_resource(result, prefixed_prop)
        return False, oaps

    # there are no more resources
    return False, []


def _get_oaps_of_one_resource(r: dict[str, Any], prefixed_prop: str | None) -> list[Oap]:
    oaps = []
    if not prefixed_prop:
        scope = create_scope_from_string(r["knora-api:hasPermissions"])
        oaps.append(Oap(scope=scope, object_iri=r["@id"]))
    elif prefixed_prop not in r:
        return []
    elif "knora-api:hasPermissions" in r[prefixed_prop]:
        scope = create_scope_from_string(r[prefixed_prop]["knora-api:hasPermissions"])
        oaps.append(Oap(scope=scope, object_iri=r[prefixed_prop]["@id"]))
    else:
        scopes = [create_scope_from_string(x["knora-api:hasPermissions"]) for x in r[prefixed_prop]]
        ids = [x["@id"] for x in r[prefixed_prop]]
        oaps.extend([Oap(scope=s, object_iri=i) for s, i in zip(scopes, ids)])
    return oaps


def get_resource(resource_iri: str, dsp_client: DspClient) -> dict[str, Any]:
    """Requests the resource with the given IRI from DSP-API"""
    iri = quote_plus(resource_iri, safe="")
    try:
        return dsp_client.get(f"/v2/resources/{iri}")
    except ApiError as err:
        err.message = f"Error while getting resource {resource_iri}"
        raise err from None


def get_oap_by_resource_iri(resource_iri: str, dsp_client: DspClient) -> Oap:
    resource = get_resource(resource_iri, dsp_client)
    scope = create_scope_from_string(resource["knora-api:hasPermissions"])
    return Oap(scope=scope, object_iri=resource_iri)


def get_all_value_oaps_of_project(shortcode: str, dsp_client: DspClient, prefixed_prop: str) -> list[Oap]:
    logger.info("******* Retrieving all value OAPs... *******")
    value_oaps = _get_all_oaps_of_project(shortcode, dsp_client, prefixed_prop=prefixed_prop)
    logger.info(f"Retrieved a TOTAL of {len(value_oaps)} value OAPs")
    return value_oaps


def get_all_resource_oaps_of_project(
    shortcode: str,
    dsp_client: DspClient,
    excluded_class_iris: Iterable[str] = (),
) -> list[Oap]:
    logger.info("******* Retrieving all resource OAPs... *******")
    resource_oaps = _get_all_oaps_of_project(shortcode, dsp_client, excluded_class_iris=excluded_class_iris)
    logger.info(f"Retrieved a TOTAL of {len(resource_oaps)} resource OAPs")
    return resource_oaps


def _get_all_oaps_of_project(
    shortcode: str, dsp_client: DspClient, excluded_class_iris: Iterable[str] = (), prefixed_prop: str | None = None
) -> list[Oap]:
    project_iri, onto_iris = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    all_oaps = []
    resclass_iris = get_all_resource_class_iris_of_project(onto_iris, dsp_client)
    resclass_iris = [x for x in resclass_iris if x not in excluded_class_iris]
    for resclass_iri in resclass_iris:
        oaps = _get_all_oaps_of_resclass(resclass_iri, project_iri, dsp_client, prefixed_prop)
        all_oaps.extend(oaps)
    return all_oaps
