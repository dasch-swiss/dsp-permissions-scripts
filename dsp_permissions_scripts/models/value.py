from dataclasses import dataclass


@dataclass
class ValueUpdate:
    """
    DTO for updating a value.
    Contains the property whith which the value relates to its resource,
    the value IRI and the value type.
    """

    property: str
    value_iri: str
    value_type: str
