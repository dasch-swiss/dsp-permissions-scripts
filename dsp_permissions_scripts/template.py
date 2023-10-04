from dotenv import load_dotenv

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.permission import Doap, Oap
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.doap_get import (
    get_doaps_of_project,
    print_doaps_of_project,
)
from dsp_permissions_scripts.utils.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.utils.oap import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    for oap in oaps:
        oap.scope.D.append(BuiltinGroup.PROJECT_MEMBER)
    return oaps


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    for doap in doaps: 
        if doap.target.group in [BuiltinGroup.PROJECT_MEMBER.value, BuiltinGroup.PROJECT_ADMIN.value]:
            doap.scope = PUBLIC
    return doaps


def main() -> None:
    """
    The main method assembles a sample call of all available high-level functions.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("test")
    shortcode = "F18E"
    token = login(host)

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
    resource_oaps = get_all_resource_oaps_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    resource_oaps_updated = modify_oaps(oaps=resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_updated,
        host=host,
        token=token,
    )


if __name__ == "__main__":
    main()
