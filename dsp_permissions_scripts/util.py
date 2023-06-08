
from urllib.parse import quote_plus


def url_encode(iri: str) -> str:
    """
    Encodes an IRI for use in a URL.
    """
    return quote_plus(iri, safe='')
