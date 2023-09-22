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
