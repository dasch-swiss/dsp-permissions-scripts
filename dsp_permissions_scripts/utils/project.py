from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.models.permission import Oap
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.permissions import permission_string_as_marshal_scope


def get_project_iri_by_shortcode(shortcode: str, host: str) -> str:
    """
    Retrieves the IRI of a project by its shortcode.
    """
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/projects/shortcode/{shortcode}"
    response = requests.get(url, timeout=5)
    assert response.status_code == 200
    iri: str = response.json()["project"]["id"]
    return iri


def get_all_resources_of_project(
    project_iri: str, 
    host: str,
    token: str,
) -> list[Oap]:
    all_resources = []
    resclasses = __get_all_resource_classes_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    for resclass in resclasses:
        resources = __get_all_resources_of_resclass(
            host=host,
            resclass=resclass,
            project_iri=project_iri,
            token=token,
        )
        all_resources.extend(resources)
    return all_resources


def __get_all_resource_classes_of_project(
    project_iri: str, 
    host: str,
    token: str,
) -> list[str]:
    project_onto_iris = __get_onto_iris_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    all_class_iris = []
    for onto_iri in project_onto_iris:
        class_iris = __get_class_iris_of_onto(
            host=host,
            onto_iri=onto_iri,
            token=token,
        )
        all_class_iris.extend(class_iris)
    return all_class_iris


def __get_onto_iris_of_project(
    project_iri: str, 
    host: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/ontologies/metadata"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    all_ontologies = response.json().get("@graph")
    project_onto_iris = [o["@id"] for o in all_ontologies if o["knora-api:attachedToProject"]["@id"] == project_iri]
    return project_onto_iris


def __get_class_iris_of_onto(
    host: str,
    onto_iri: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/ontologies/allentities/{quote_plus(onto_iri)}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    all_entities = response.json()["@graph"]
    context = response.json()["@context"]
    class_ids = [c["@id"] for c in all_entities if c.get("knora-api:isResourceClass")]
    class_iris = [__dereference_prefix(class_id, context) for class_id in class_ids]
    return class_iris


def __dereference_prefix(identifier: str, context: dict[str, str]) -> str:
    prefix, actual_id = identifier.split(":")
    return context[prefix] + actual_id


def __get_all_resources_of_resclass(
    host: str, 
    resclass: str,
    project_iri: str,
    token: str,
) -> list[Oap]:
    protocol = get_protocol(host)
    headers = {"X-Knora-Accept-Project": project_iri, "Authorization": f"Bearer {token}"}
    resources: list[str] = []
    page = 0
    more = True
    while more:
        more, iris = __get_next_page(
            protocol=protocol,
            host=host,
            resclass=resclass,
            page=page,
            headers=headers,
        )
        resources.extend(iris)
        page += 1
    return resources


def __get_next_page(
    protocol: str,
    host: str,
    resclass: str,
    page: int,
    headers: dict[str, str],
) -> tuple[bool, list[str]]:
    """
    Get the resource IRIs of a resource class, one page at a time.
    DSP-API returns results page-wise: 
    a list of 25 resources if there are 25 resources or more,
    a list of less than 25 resources if there are less than 25 remaining,
    1 resource (not packed in a list) if there is only 1 remaining,
    and an empty response content with status code 200 if there are no resources remaining.
    This means that the page must be incremented until the response contains 0 or 1 resource.
    """
    url = f"{protocol}://{host}/v2/resources?resourceClass={quote_plus(resclass)}&page={page}"
    response = requests.get(url, headers=headers, timeout=5)
    assert response.status_code == 200
    result = response.json()
    if "@graph" in result:
        # result contains several resources: return them, then continue with next page
        oaps = []
        for r in result["@graph"]:
            scope=permission_string_as_marshal_scope(r["knora-api:hasPermissions"])
            oaps.append(Oap(scope=scope, object_iri=r["@id"]))
        return True, oaps
    elif "@id" in result:
        # result contains only 1 resource: return it, then stop (there will be no more resources)
        scope=permission_string_as_marshal_scope(result["knora-api:hasPermissions"])
        return False, [Oap(scope=scope, object_iri=result["@id"]), ]
    else:
        # there are no more resources
        return False, []
