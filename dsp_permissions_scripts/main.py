
from dotenv import load_dotenv

from dsp_permissions_scripts.utils.authentication import get_env, get_token
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.permission import PermissionScope
from dsp_permissions_scripts.models.scope import Scope
from dsp_permissions_scripts.utils.permissions import (
    update_doap_scope,
    update_permissions_for_resources_and_values,
    get_doaps_for_project
)
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode


def main() -> None:
    """
    Currently, 3 actions are supported:

    1. print the doaps for a project
    2. set the object access permissions for a list of objects (resources/properties) and each of their values.
    3. apply a scope (e.g. "public") to all DOAPs for the given project
    """
    host = Hosts.get_host("test")
    shortcode = "0848"
    inspect_permissions(host, shortcode)
    set_doaps(
        host=host, 
        shortcode=shortcode,
        scope=Scope.PUBLIC,
    )
    set_oaps(
        host=host,
        scope=Scope.PUBLIC,
    )


def inspect_permissions(host: str, shortcode: str) -> None:
    """
    Prints the doaps for a project, provided a host and a shortcode.
    """
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    doaps = get_doaps_for_project(project_iri, host, token)
    for d in doaps:
        print(d.json(indent=2))
        print()


def set_oaps(
    host: str,
    scope: list[PermissionScope],
) -> None:
    """
    sets the object access permissions for a list of objects (resources/properties) and each of their values.
    """
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    object_iris = [
        # "http://rdfh.ch/0810/_cyEQqI4T3-d_MIl0IAS2w",
        # "http://rdfh.ch/0810/9eUg68OWR66u26Bffrj0nQ",
        # "http://rdfh.ch/0810/bAZD7_qnSMCt9yVtTaCNqQ",
        # "http://rdfh.ch/0810/UigKXIqHSHSWomxUZ_gCvQ",
        # "http://rdfh.ch/0810/FaURJ8QaRY2TbUahi6QBog",
        # "http://rdfh.ch/0810/JYBrw1MARLKcrAHrJarrTQ",
        # "http://rdfh.ch/0810/UHJZN4OZQ7SKIpAHzeCkQw"
        "http://rdfh.ch/1234/QWh4ZIIiTuSxV0Ov3pc8ig"
    ]
    update_permissions_for_resources_and_values(
        resource_iris=object_iris, 
        scope=scope, 
        host=host, 
        token=token,
    )


def set_doaps(
    host: str, 
    shortcode: str,
    scope: list[PermissionScope],
) -> None:
    """
    Applies the given scope to all DOAPs for the given project.

    Args:
        host: the DSP server where the project is located
        shortcode: the shortcode of the project
        scope: one of the standard scopes defined in the Scope class
    """
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    doaps = get_doaps_for_project(project_iri, host, token)
    # normally there are 2 doaps: one for project admins, one for project members.
    # But there might be more groups.
    for d in doaps:
        print(d.iri, d.target, d.scope)
        update_doap_scope(
            permission_iri=d.iri, 
            scope=scope, 
            host=host, 
            token=token,
        )
    print("Finished successfully")


if __name__ == "__main__":
    # set login credentials from .env file as environment variables
    load_dotenv()
    main()
