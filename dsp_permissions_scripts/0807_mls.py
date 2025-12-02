import copy

from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import apply_updated_scopes_of_aps_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import OPEN
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_aps(aps: list[Ap]) -> list[Ap]:
    """Adapt this sample to your needs."""
    modified_aps = []
    for ap in copy.deepcopy(aps):
        ap.add_permission(ApValue.ProjectAdminAllPermission)
        ap.remove_permission(ApValue.ProjectResourceCreateAllPermission)
        modified_aps.append(ap)
    return modified_aps


def update_aps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    modified_aps = modify_aps(project_aps)
    if not modified_aps:
        logger.info("There are no APs to update.")
        return
    apply_updated_scopes_of_aps_on_server(modified_aps, dsp_client)
    project_aps_updated = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps_updated,
        shortcode=shortcode,
        mode="modified",
        server=dsp_client.server,
    )


def update_doaps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.PROJECT_ADMIN),
        shortcode=shortcode,
        scope=OPEN,
        dsp_client=dsp_client,
    )
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.PROJECT_MEMBER),
        shortcode=shortcode,
        scope=OPEN,
        dsp_client=dsp_client,
    )
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        server=dsp_client.server,
    )


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("rdu")
    shortcode = "0807"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_aps(shortcode=shortcode, dsp_client=dsp_client)
    update_doaps(shortcode=shortcode, dsp_client=dsp_client)


if __name__ == "__main__":
    main()
