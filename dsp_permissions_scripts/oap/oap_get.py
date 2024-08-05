import copy
import re
from typing import Any
from urllib.parse import quote
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import dereference_prefix
from dsp_permissions_scripts.utils.project import get_all_resource_class_localnames_of_project
from dsp_permissions_scripts.utils.project import get_project_iri_and_onto_iris_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string

logger = get_logger(__name__)

IGNORE_KEYS = [
    "@id",
    "@type",
    "@context",
    "rdfs:label",
    "knora-api:DeletedValue",
    "knora-api:lastModificationDate",
    "knora-api:creationDate",
    "knora-api:arkUrl",
    "knora-api:versionArkUrl",
    "knora-api:attachedToProject",
    "knora-api:attachedToUser",
    "knora-api:userHasPermission",
    "knora-api:hasPermissions",
]
KB_RESCLASSES = [
    "knora-api:VideoSegment",
    "knora-api:AudioSegment",
    "knora-api:Region",
    "knora-api:Annotation",
    "knora-api:LinkObj",
]


def get_oaps_of_kb_resclasses(dsp_client: DspClient, project_iri: str, oap_config: OapRetrieveConfig) -> list[Oap]:
    match oap_config.retrieve_resources:
        case "specified_res_classes":
            specified_kb_resclasses = [x for x in KB_RESCLASSES if x in oap_config.specified_res_classes]
            res_only_oaps = _get_oaps_of_specified_kb_resclasses(dsp_client, project_iri, specified_kb_resclasses)
        case "all":
            res_only_oaps = _get_oaps_of_specified_kb_resclasses(dsp_client, project_iri, KB_RESCLASSES)

    match oap_config.retrieve_values:
        case "none":
            return res_only_oaps
        case "specified_props":
            enriched_oaps = _enrich_with_value_oaps(dsp_client, res_only_oaps, oap_config.specified_props)
        case "all":
            enriched_oaps = _enrich_with_value_oaps(dsp_client, res_only_oaps)

    return enriched_oaps


def _get_oaps_of_specified_kb_resclasses(
    dsp_client: DspClient, project_iri: str, kb_resclasses: list[str]
) -> list[Oap]:
    all_oaps: list[Oap] = []
    for resclass in kb_resclasses:
        all_oaps.extend(_get_oaps_of_one_kb_resclass(dsp_client, project_iri, resclass))
    return all_oaps


def _enrich_with_value_oaps(
    dsp_client: DspClient, res_only_oaps: list[Oap], restrict_to_props: list[str] | None = None
) -> list[Oap]:
    complete_oaps = copy.deepcopy(res_only_oaps)
    for oap in complete_oaps:
        full_resource = dsp_client.get(f"/v2/resources/{quote_plus(oap.resource_oap.resource_iri)}")  # type: ignore[union-attr]
        oap.value_oaps = _get_value_oaps(full_resource, restrict_to_props)
    return complete_oaps


def _get_oaps_of_one_kb_resclass(dsp_client: DspClient, project_iri: str, resclass: str) -> list[Oap]:
    oaps: list[Oap] = []
    mayHaveMoreResults: bool = True
    offset = 0
    while mayHaveMoreResults:
        sparql_query = """
        PREFIX knora-api: <http://api.knora.org/ontology/knora-api/v2#>

        CONSTRUCT {
            ?kb_resclass knora-api:isMainResource true .
        } WHERE {
            BIND(<%(project_iri)s> as ?project_iri) .
            ?kb_resclass a %(resclass)s .
            ?kb_resclass knora-api:attachedToProject ?project_iri .
        }
        OFFSET %(offset)s
        """ % {"resclass": resclass, "project_iri": project_iri, "offset": offset}  # noqa: UP031 (printf-string-formatting)
        sparql_query_stripped = re.sub(r"\s+", " ", sparql_query).strip()
        if not (response := dsp_client.get(f"/v2/searchextended/{quote(sparql_query_stripped, safe='')}")):
            break  # if there are 0 results, the response is an empty dict
        # 1 result: the resource is returned as a single dict
        # >1 results: the resource is returned as a list of dicts
        for json_resource in response.get("@graph", [response]):
            scope = create_scope_from_string(json_resource["knora-api:hasPermissions"])
            res_oap = ResourceOap(scope=scope, resource_iri=json_resource["@id"])
            oaps.append(Oap(resource_oap=res_oap, value_oaps=[]))
        mayHaveMoreResults = bool(response.get("knora-api:mayHaveMoreResults", False))
        offset += 1
    return oaps


def _get_all_oaps_of_resclass(
    resclass_localname: str, project_iri: str, dsp_client: DspClient, oap_config: OapRetrieveConfig
) -> list[Oap]:
    headers = {"X-Knora-Accept-Project": project_iri}
    all_oaps: list[Oap] = []
    page = 0
    more = True
    while more:
        logger.info(f"Getting page {page}...")
        try:
            more, oaps = _get_next_page(
                resclass_localname=resclass_localname,
                page=page,
                headers=headers,
                dsp_client=dsp_client,
                oap_config=oap_config,
            )
            all_oaps.extend(oaps)
            page += 1
        except ApiError as err:
            logger.error(f"{err}\nStop getting more pages, return what has been retrieved so far.")
            more = False
    logger.info(f"Retrieved {len(all_oaps)} OAPs of class {resclass_localname}")
    return all_oaps


def _get_next_page(
    resclass_localname: str,
    page: int,
    headers: dict[str, str],
    dsp_client: DspClient,
    oap_config: OapRetrieveConfig,
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
    resclass_iri = dereference_prefix(resclass_localname, oap_config.context)
    route = f"/v2/resources?resourceClass={quote_plus(resclass_iri)}&page={page}"
    try:
        result = dsp_client.get(route, headers=headers)
    except ApiError as err:
        err.message = "Could not get next page"
        raise err from None

    # result contains several resources: return them, then continue with next page
    if "@graph" in result:
        oaps = []
        for r in result["@graph"]:
            if oap := _get_oap_of_one_resource(r, oap_config):
                oaps.append(oap)
        return True, oaps

    # result contains only 1 resource: return it, then stop (there will be no more resources)
    if "@id" in result:
        oaps = []
        if oap := _get_oap_of_one_resource(result, oap_config):
            oaps.append(oap)
        return False, oaps

    # there are no more resources
    return False, []


def _get_oap_of_one_resource(r: dict[str, Any], oap_config: OapRetrieveConfig) -> Oap | None:
    if oap_config.retrieve_resources != "all" and r["@type"] not in oap_config.specified_res_classes:
        return None
    scope = create_scope_from_string(r["knora-api:hasPermissions"])
    resource_oap = ResourceOap(scope=scope, resource_iri=r["@id"])

    if oap_config.retrieve_values == "none":
        value_oaps = []
    elif oap_config.retrieve_values == "all":
        value_oaps = _get_value_oaps(r)
    else:
        value_oaps = _get_value_oaps(r, oap_config.specified_props)

    return Oap(resource_oap=resource_oap, value_oaps=value_oaps)


def _get_value_oaps(resource: dict[str, Any], restrict_to_props: list[str] | None = None) -> list[ValueOap]:
    res = []
    for k, v in resource.items():
        if k in IGNORE_KEYS:
            continue
        if restrict_to_props is not None and k not in restrict_to_props:
            continue
        values = v if isinstance(v, list) else [v]
        for val in values:
            if not isinstance(val, dict) or val.get("knora-api:isDeleted"):
                continue
            match val:
                case {
                    "@id": id_,
                    "@type": type_,
                    "knora-api:hasPermissions": perm_str,
                } if "/values/" in id_:
                    scope = create_scope_from_string(perm_str)
                    oap = ValueOap(
                        scope=scope, property=k, value_type=type_, value_iri=id_, resource_iri=resource["@id"]
                    )
                    res.append(oap)
                case _:
                    continue
    return res


def get_all_oaps_of_project(
    shortcode: str,
    dsp_client: DspClient,
    oap_config: OapRetrieveConfig,
) -> list[Oap]:
    logger.info("******* Retrieving all OAPs... *******")
    project_iri, onto_iris = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    resclass_localnames = get_all_resource_class_localnames_of_project(onto_iris, dsp_client, oap_config)
    all_oaps: list[Oap] = []
    for resclass_localname in resclass_localnames:
        oaps = _get_all_oaps_of_resclass(resclass_localname, project_iri, dsp_client, oap_config)
        all_oaps.extend(oaps)
    all_oaps.extend(get_oaps_of_kb_resclasses(dsp_client, project_iri, oap_config))
    logger.info(f"Retrieved a TOTAL of {len(all_oaps)} OAPs")
    return all_oaps
