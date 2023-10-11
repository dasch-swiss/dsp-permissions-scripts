from dotenv import load_dotenv

from dsp_permissions_scripts.models.doap import Doap
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.oap import Oap
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.doap_get import (
    get_doaps_of_project,
    print_doaps_of_project,
)
from dsp_permissions_scripts.utils.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.utils.oap import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def fix_scenario_tanner() -> None:
    """
    Adapt the project Scenario Tanner on prod:
    Remove ProjectMember from Modify, and add it to View.
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


def fix_doaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    project_doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    print_doaps_of_project(
        doaps=project_doaps,
        host=host,
        shortcode=shortcode,
    )
    project_doaps_updated = modify_doaps(doaps=project_doaps)
    apply_updated_doaps_on_server(
        doaps=project_doaps_updated,
        host=host,
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
    resource_oaps_updated = modify_oaps(oaps=all_resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_updated,
        host=host,
        token=token,
    )


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Remove ProjectMember from Modify, and add it to View."""
    for d in doaps:
        d.scope = d.scope.remove("M", BuiltinGroup.PROJECT_MEMBER)
        d.scope = d.scope.add("V", BuiltinGroup.PROJECT_MEMBER)
    return doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Remove ProjectMember from Modify, and add it to View."""
    for oap in oaps:
        oap.scope = oap.scope.remove("M", BuiltinGroup.PROJECT_MEMBER)
        oap.scope = oap.scope.add("V", BuiltinGroup.PROJECT_MEMBER)
    return oaps


if __name__ == "__main__":
    fix_scenario_tanner()
