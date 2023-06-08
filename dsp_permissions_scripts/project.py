import requests


def get_project_iri_by_shortcode(shortcode: str, host: str) -> str:
    url = f"https://{host}/admin/projects/shortcode/{shortcode}"
    response = requests.get(url)
    assert response.status_code == 200
    iri: str = response.json()["project"]["id"]
    return iri
