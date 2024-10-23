PACKAGE_NAME = "dsp-permissions-scripts"
KNORA_ADMIN_ONTO_NAMESPACE = "http://www.knora.org/ontology/knora-admin#"


def dereference_prefix(
    identifier: str,
    context: dict[str, str],
) -> str:
    """
    Replaces the prefix of an identifier by what the prefix stands for,
    and returns the full IRI of the given identifier.

    Args:
        identifier: an identifier, e.g. "knora-admin:Creator"
        context: The context to use for dereferencing

    Returns:
        The full IRI of the given identifier, e.g. "http://www.knora.org/ontology/knora-admin#Creator"
    """
    namespace_prefix, localname = identifier.split(":")
    return context[namespace_prefix] + localname
