import copy
import re
from urllib.parse import quote
from urllib.parse import quote_plus

from dsp_permissions_scripts.oap.oap_get import get_value_oaps
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.scope_serialization import create_scope_from_string

KB_RESCLASSES = [
    "knora-api:VideoSegment",
    "knora-api:AudioSegment",
    "knora-api:Region",
    "knora-api:Annotation",
    "knora-api:LinkObj",
]


def get_oaps_of_kb_resclasses(dsp_client: DspClient, project_iri: str, oap_config: OapRetrieveConfig) -> list[Oap]:
    match oap_config.retrieve_resources:
        case "none":
            return []
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
        oap.value_oaps = get_value_oaps(full_resource, restrict_to_props)
    return complete_oaps


def _get_oaps_of_one_kb_resclass(dsp_client: DspClient, project_iri: str, resclass: str) -> list[Oap]:
    oaps: list[Oap] = []
    mayHaveMoreResults: bool = True
    offset = 0
    while mayHaveMoreResults:
        sparql_query = """
        PREFIX knora-api: <http://api.knora.org/ontology/knora-api/v2#>

        CONSTRUCT {
            ?linkobj knora-api:isMainResource true .
        } WHERE {
            BIND(<%(project_iri)s> as ?project_iri) .
            ?linkobj a %(resclass)s .
            ?linkobj knora-api:attachedToProject ?project_iri .
        }
        OFFSET %(offset)s
        """ % {"resclass": resclass, "project_iri": project_iri, "offset": offset}  # noqa: UP031 (printf-string-formatting)
        sparql_query_stripped = re.sub(r"\s+", " ", sparql_query).strip()
        if not (response := dsp_client.get(f"/v2/searchextended/{quote(sparql_query_stripped, safe='')}")):
            break  # if there are 0 results, the response is an empty dict
        for json_resource in response.get("@graph", [response]):
            scope = create_scope_from_string(json_resource["knora-api:hasPermissions"])
            res_oap = ResourceOap(scope=scope, resource_iri=json_resource["@id"])
            oaps.append(Oap(resource_oap=res_oap, value_oaps=[]))
        mayHaveMoreResults = bool(response.get("knora-api:mayHaveMoreResults", False))
        offset += 1
    return oaps
