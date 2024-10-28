from dsp_permissions_scripts.ap.ap_delete import delete_ap_of_group_on_server
from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.doap.doap_delete import _delete_doap_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models.group import KNOWN_USER
from dsp_permissions_scripts.models.group import PROJECT_ADMIN
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import UNKNOWN_USER
from dsp_permissions_scripts.models.group import group_builder
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

LIMC_OPEN = PermissionScope.create(
    CR=[PROJECT_ADMIN],
    D=[group_builder("limc:limc-editors")],
    V=[PROJECT_MEMBER, KNOWN_USER, UNKNOWN_USER],
)

logger = get_logger(__name__)


def update_aps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    _ = delete_ap_of_group_on_server(
        existing_aps=project_aps,
        forGroup=PROJECT_MEMBER,
        dsp_client=dsp_client,
    )
    _ = create_new_ap_on_server(
        forGroup=group_builder("limc:limc-editors"),
        shortcode=shortcode,
        hasPermissions=[ApValue.ProjectResourceCreateAllPermission],
        dsp_client=dsp_client,
    )
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
    for doap in project_doaps:
        _delete_doap_on_server(doap, dsp_client)
        logger.info(f"Deleted DOAP {doap.doap_iri}")
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=PROJECT_ADMIN),
        shortcode=shortcode,
        scope=LIMC_OPEN,
        dsp_client=dsp_client,
    )
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group_builder("limc:limc-editors")),
        shortcode=shortcode,
        scope=LIMC_OPEN,
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
    shortcode = "080E"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_aps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )
    update_doaps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
