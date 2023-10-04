from dotenv import load_dotenv

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.doap_get import (
    get_doaps_of_project,
    print_doaps_of_project,
)
from dsp_permissions_scripts.utils.doap_set import __update_doap_scope
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def fix_scenario_tanner() -> None:
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
    all_resource_oaps = get_all_resource_oaps_of_project(
        shortcode=shortcode,
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
    for d in doaps:
        d.scope.V.append("http://rdfh.ch/groups/0102/oe8-uWCgS4Wl6wfOvaFGCA")
    new_doaps = []
    for d in doaps:
        new_doap = __update_doap_scope(
            doap_iri=d.doap_iri,
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
    fix_scenario_tanner()
