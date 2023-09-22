from typing import Sequence

from dotenv import load_dotenv

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.permission import (
    Doap,
    DoapTargetType,
    PermissionScopeElement,
)
from dsp_permissions_scripts.models.scope import StandardScope
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.permissions import (
    filter_doaps_by_target,
    get_doaps_for_project,
    get_doaps_of_groups,
    print_doaps_of_project,
    update_doap_scope,
    update_permissions_for_resources_and_values,
)
from dsp_permissions_scripts.utils.project import get_project_iri_by_shortcode


def main() -> None:
    """
    The main method assembles a sample call of all available high-level functions.
    """
    host = Hosts.get_host("test")
    shortcode = "F18E"
    token = login(host)
    
    new_scope = StandardScope().PUBLIC
    groups = [BuiltinGroup.PROJECT_ADMIN, BuiltinGroup.PROJECT_MEMBER]

    doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    print_doaps_of_project(
        doaps=doaps,
        host=host,
        shortcode=shortcode,
    )
    set_doaps_of_groups(
        scope=new_scope,
        groups=groups,
        host=host,
        shortcode=shortcode,
        token=token,
    )
    update_permissions_for_resources_and_values(
        resource_iris=["http://rdfh.ch/0810/foo", "http://rdfh.ch/0810/bar"],
        scope=new_scope,
        host=host,
        token=token,
    )


def get_doaps_of_project(
    host: str,
    shortcode: str,
    token: str,
    target: DoapTargetType = DoapTargetType.ALL,
) -> list[Doap]:
    """
    Get the doaps for a project, provided a host and a shortcode.
    Optionally, select only the DOAPs that are related to either a group, or a resource class, or a property.
    By default, all DOAPs are returned, regardless of their target (target=all).
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
    filtered_doaps = filter_doaps_by_target(
        doaps=doaps,
        target=target,
    )
    return filtered_doaps


def set_doaps_of_groups(
    scope: list[PermissionScopeElement],
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
