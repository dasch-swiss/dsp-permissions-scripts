from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.permission import PermissionScope
from dsp_permissions_scripts.models.scope import StandardScope
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.permissions import (
    get_doaps_for_project,
    get_doaps_of_groups,
    update_doap_scope,
    update_permissions_for_resources_and_values,
)
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode


def main() -> None:
    """
    Currently, 3 actions are supported:

    1. print the doaps for a project
    2. set the object access permissions for a list of objects (resources/properties)
       and each of their values.
    3. apply a scope (e.g. "public") to all DOAPs for the given project
    """
    host = Hosts.get_host("test")
    shortcode = "F18E"
    new_scope = StandardScope().PUBLIC
    groups = [BuiltinGroup.PROJECT_ADMIN, BuiltinGroup.PROJECT_MEMBER]
    token = login(host)
    print_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    set_doaps_of_groups(
        scope=new_scope,
        groups=groups,
        host=host,
        shortcode=shortcode,
        token=token,
    )
    set_oaps(
        host=host,
        scope=new_scope,
        token=token,
        resources_filepath="resource_iris.txt",
    )


def print_doaps_of_project(
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
    heading = f"Project {shortcode} on server {host} has {len(doaps)} DOAPs"
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for d in doaps:
        print(d.model_dump_json(indent=2))
        print()


def set_oaps(
    host: str,
    scope: list[PermissionScope],
    token: str,
    resources_filepath: str | Path,
) -> None:
    """
    Reads resource IRIs from a txt file,
    and sets the object access permissions
    for all resources and each of their values.
    """
    with open(resources_filepath, "r", encoding="utf-8") as f:
        resource_iris = [s.strip("\n") for s in f.readlines()]
    update_permissions_for_resources_and_values(
        resource_iris=resource_iris,
        scope=scope,
        host=host,
        token=token,
    )


def set_doaps_of_groups(
    scope: list[PermissionScope],
    groups: Sequence[str | BuiltinGroup],
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """
    Applies the given scope to the DOAPs of the given groups.

    Args:
        scope: one of the standard scopes defined in the Scope class
        groups: the group IRIs to whose DOAP the scope should be applied
        host: the DSP server where the project is located
        shortcode: the shortcode of the project
        token: the access token
    """
    applicable_doaps = get_doaps_of_groups(
        groups=groups,
        host=host,
        shortcode=shortcode,
        token=token,
    )
    heading = f"Update {len(applicable_doaps)} DOAPs on {host}..."
    print(f"\n{heading}\n{'=' * len(heading)}\n")
    for d in applicable_doaps:
        print("Old DOAP:\n=========")
        print(d.model_dump_json(indent=2))
        new_doap = update_doap_scope(
            permission_iri=d.iri,
            scope=scope,
            host=host,
            token=token,
        )
        print("\nNew DOAP:\n=========")
        print(new_doap.model_dump_json(indent=2))
        print()
    print("All DOAPs have been updated.")


if __name__ == "__main__":
    load_dotenv()  # set login credentials from .env file as environment variables
    main()
