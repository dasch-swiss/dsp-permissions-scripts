from dataclasses import dataclass


@dataclass
class ValueUpdate:
    property: str
    value_iri: str
    value_type: str
