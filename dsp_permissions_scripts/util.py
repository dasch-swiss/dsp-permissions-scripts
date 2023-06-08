
from urllib.parse import quote_plus


def url_encode(iri: str) -> str:
    return quote_plus(iri, safe='')
