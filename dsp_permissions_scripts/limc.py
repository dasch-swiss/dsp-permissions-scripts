import copy

from dsp_permissions_scripts.ap.ap_delete import delete_ap_of_group_on_server
from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_scopes_of_doaps_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in copy.deepcopy(doaps):
        if doap.target.group == group.UNKNOWN_USER:
            doap.scope = PUBLIC
            modified_doaps.append(doap)
    return modified_doaps


def update_aps(host: str, shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    _ = delete_ap_of_group_on_server(
        host=host,
        existing_aps=project_aps,
        forGroup=group.PROJECT_MEMBER,
        dsp_client=dsp_client,
    )
    _ = create_new_ap_on_server(
        forGroup="limc:limc-editors",
        shortcode=shortcode,
        hasPermissions=[ApValue.ProjectResourceCreateAllPermission],
        dsp_client=dsp_client,
    )
    project_aps_updated = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def update_doaps(host: str, shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    # remove the doap for the ProjectMember (he cannot create resources, anyway)
    # modify doap of ProjectAdmin:
    #    - Creator: CR
    #    - ProjectAdmin: CR
    #    - limc:limc-editors: D
    #    - ProjectMember: V
    #    - KnownUser: V
    #    - UnknownUser: V
    # create a new doap for limc:limc-editors (the same doap as above for ProjectAdmin)
    project_doaps_modified = modify_doaps(doaps=project_doaps)
    if not project_doaps_modified:
        logger.info("There are no DOAPs to update.")
        return
    apply_updated_scopes_of_doaps_on_server(project_doaps_modified, host, dsp_client)
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("rdu-07")
    shortcode = "080E"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_aps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
    )
    update_doaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
