# pylint: disable=duplicate-code

from dotenv import load_dotenv

from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import delete_ap
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.models import builtin_groups
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.oap.oap_get_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Remove ProjectMember from Modify, and add it to View."""
    for d in doaps:
        d.scope = d.scope.remove("M", builtin_groups.PROJECT_MEMBER)
        d.scope = d.scope.add("V", builtin_groups.PROJECT_MEMBER)
    return doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Remove ProjectMember from Modify, and add it to View."""
    for oap in oaps:
        oap.scope = oap.scope.remove("M", builtin_groups.PROJECT_MEMBER)
        oap.scope = oap.scope.add("V", builtin_groups.PROJECT_MEMBER)
    return oaps


def update_aps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """Delete the Administrative Permission that allows the ProjectMember to create resources."""
    project_aps = get_aps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
    )
    _ = delete_ap(
        host=host,
        token=token,
        existing_aps=project_aps,
        forGroup=builtin_groups.PROJECT_MEMBER,
    )
    project_aps_updated = get_aps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_aps_of_project(
        project_aps=project_aps_updated,
        shortcode=shortcode,
        mode="modified",
    )


def update_doaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    project_doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
    )
    project_doaps_modified = modify_doaps(doaps=project_doaps)
    apply_updated_doaps_on_server(
        doaps=project_doaps_modified,
        host=host,
        token=token,
    )
    project_doaps_updated = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
    )


def update_oaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    resource_oaps = get_all_resource_oaps_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    serialize_resource_oaps(
        resource_oaps=resource_oaps,
        shortcode=shortcode,
        mode="original",
    )
    resource_oaps_modified = modify_oaps(oaps=resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_modified,
        host=host,
        token=token,
        shortcode=shortcode,
    )
    resource_oaps_updated = get_all_resource_oaps_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    serialize_resource_oaps(
        resource_oaps=resource_oaps_updated,
        shortcode=shortcode,
        mode="modified",
    )


def fix_scenario_tanner() -> None:
    """
    Adapt the project Scenario Tanner on prod:
    Revoke Modify rights from ProjectMember, and grant them View rights.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("stage")
    shortcode = "0102"
    token = login(host)

    update_aps(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    update_doaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    update_oaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )


if __name__ == "__main__":
    fix_scenario_tanner()
