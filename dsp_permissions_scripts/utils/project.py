from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.utils.authentication import get_protocol


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


def get_all_resource_iris_of_project(
    project_iri: str, 
    host: str,
    token: str,
) -> list[str]:
    all_resource_iris = []
    resclasses = __get_all_resource_classes_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    for resclass in resclasses:
        resource_iris = __get_all_resource_iris_of_resclass(
            host=host,
            resclass=resclass,
            project_iri=project_iri,
            token=token,
        )
        all_resource_iris.extend(resource_iris)
    return all_resource_iris


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


def __get_all_resource_iris_of_resclass(
    host: str, 
    resclass: str,
    project_iri: str,
    token: str,
) -> list[str]:
    protocol = get_protocol(host)
    headers = {"X-Knora-Accept-Project": project_iri, "Authorization": f"Bearer {token}"}
    resource_iris = []
    page = 0
    while True:
        url = f"{protocol}://{host}/v2/resources?resourceClass={quote_plus(resclass)}&page={page}"
        response = requests.get(url, headers=headers, timeout=5)
        assert response.status_code == 200
        result = response.json()
        if "@graph" in result:
            # result contains several resources: store them, then continue with next page
            resource_iris.extend([r["@id"] for r in result["@graph"]])
        elif "@id" in result:
            # result contains only 1 resource: store it, then stop (there will be no more resources)
            resource_iris.append(result["@id"])
            break
        else:
            break  # there are no more resources
        page += 1
    return resource_iris
