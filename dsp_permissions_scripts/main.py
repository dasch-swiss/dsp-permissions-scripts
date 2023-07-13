
from dotenv import load_dotenv

from dsp_permissions_scripts.utils.authentication import login
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
    new_scope = Scope.PUBLIC
    token = login(host)
    print_doaps(
        host=host, 
        shortcode=shortcode,
        token=token,
    )
    set_doaps(
        host=host, 
        shortcode=shortcode,
        scope=new_scope,
        token=token,
    )
    set_oaps(
        host=host,
        scope=new_scope,
        token=token,
    )


def print_doaps(
    host: str, 
    shortcode: str,
    token: str,
) -> None:
    """
    Print the doaps for a project, provided a host and a shortcode.
    """
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode, 
        host=host,
    )
    doaps = get_doaps_for_project(
        project_iri=project_iri, 
        host=host, 
        token=token,
    )
    for d in doaps:
        print(d.json(indent=2))
        print()


def set_oaps(
    host: str,
    scope: list[PermissionScope],
    token: str,
) -> None:
    """
    sets the object access permissions for a list of objects (resources/properties) and each of their values.
    """
    object_iris = [
        "http://rdfh.ch/0810/foo",
        "http://rdfh.ch/0810/bar",
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
    token: str,
) -> None:
    """
    Applies the given scope to all DOAPs for the given project.

    Args:
        host: the DSP server where the project is located
        shortcode: the shortcode of the project
        scope: one of the standard scopes defined in the Scope class
    """
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
