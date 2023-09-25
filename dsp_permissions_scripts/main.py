from dotenv import load_dotenv

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.permission import PermissionScopeElement
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.permissions import (
    get_doaps_of_project,
    print_doaps_of_project,
    update_doap_scope,
)
from dsp_permissions_scripts.utils.project import (
    get_all_resource_iris_of_project,
    get_project_iri_by_shortcode,
)


def main() -> None:
    """
    Fix the DOAPs of the scenario Tanner.
    Later, fix the OAPs.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("stage")
    shortcode = "0102"
    token = login(host)
    fix_doaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    fix_oaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )


def fix_oaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    project_iri = get_project_iri_by_shortcode(
        shortcode=shortcode,
        host=host,
    )
    all_resource_iris = get_all_resource_iris_of_project(
        project_iri=project_iri,
        host=host,
        token=token,
    )
    

def fix_doaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
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
    group_scenario_tanner_scope = PermissionScopeElement(
        info="http://rdfh.ch/groups/0102/oe8-uWCgS4Wl6wfOvaFGCA",
        name="V",
    )
    for d in doaps:
        d.scope.append(group_scenario_tanner_scope)
    new_doaps = []
    for d in doaps:
        new_doap = update_doap_scope(
            permission_iri=d.iri,
            scope=d.scope,
            host=host,
            token=token,
        )
        new_doaps.append(new_doap)
    print("\nNew DOAPs:\n=========")
    print_doaps_of_project(
        doaps=new_doaps,
        host=host,
        shortcode=shortcode,
    )


if __name__ == "__main__":
    main()
