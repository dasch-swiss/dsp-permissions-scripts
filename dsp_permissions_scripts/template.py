import copy

from dsp_permissions_scripts.ap.ap_delete import delete_ap_of_group_on_server
from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import apply_updated_scopes_of_aps_on_server
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.doap.doap_delete import delete_doap_of_group_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_scopes_of_doaps_on_server
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import OPEN
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import get_all_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import ModifiedOap
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_serialize import serialize_oaps
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_aps(aps: list[Ap]) -> list[Ap]:
    """Adapt this sample to your needs."""
    modified_aps = []
    for ap in copy.deepcopy(aps):
        if ap.forGroup == group.PROJECT_ADMIN:
            if ApValue.ProjectAdminRightsAllPermission not in ap.hasPermissions:
                ap.add_permission(ApValue.ProjectAdminRightsAllPermission)
                modified_aps.append(ap)
    return modified_aps


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in copy.deepcopy(doaps):
        if isinstance(doap.target, GroupDoapTarget) and doap.target.group == group.PROJECT_ADMIN:
            doap.scope = OPEN
            modified_doaps.append(doap)
    return modified_doaps


def modify_oaps(oaps: list[Oap]) -> list[ModifiedOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ModifiedOap] = []
    for oap in copy.deepcopy(oaps):
        new_oap = ModifiedOap()
        if oap.resource_oap.scope != OPEN:
            new_oap.resource_oap = oap.resource_oap.model_copy(update={"scope": OPEN})
        for value_oap in oap.value_oaps:
            if value_oap.scope != OPEN:
                new_oap.value_oaps.append(value_oap.model_copy(update={"scope": OPEN}))
        if not new_oap.is_empty():
            modified_oaps.append(new_oap)
    return modified_oaps


def update_aps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    remaining_aps = delete_ap_of_group_on_server(
        existing_aps=project_aps,
        forGroup=group.PROJECT_MEMBER,
        dsp_client=dsp_client,
    )
    _ = create_new_ap_on_server(
        forGroup=group.CREATOR,
        shortcode=shortcode,
        hasPermissions=[ApValue.ProjectResourceCreateAllPermission],
        dsp_client=dsp_client,
    )
    modified_aps = modify_aps(remaining_aps)
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
    remaining_doaps = delete_doap_of_group_on_server(
        existing_doaps=project_doaps,
        forGroup=group.PROJECT_MEMBER,
        dsp_client=dsp_client,
    )
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.CREATOR),
        shortcode=shortcode,
        scope=PermissionScope.create(CR=[group.SYSTEM_ADMIN]),
        dsp_client=dsp_client,
    )
    project_doaps_modified = modify_doaps(doaps=remaining_doaps)
    if not project_doaps_modified:
        logger.info("There are no DOAPs to update.")
        return
    apply_updated_scopes_of_doaps_on_server(project_doaps_modified, dsp_client)
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        server=dsp_client.server,
    )


def update_oaps(shortcode: str, dsp_client: DspClient, oap_config: OapRetrieveConfig) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    oaps = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
    serialize_oaps(oaps, shortcode, mode="original")
    oaps_modified = modify_oaps(oaps)
    if not oaps_modified:
        logger.info("There are no OAPs to update.")
        return
    apply_updated_oaps_on_server(
        oaps=oaps_modified,
        shortcode=shortcode,
        dsp_client=dsp_client,
        nthreads=4,
    )
    oaps_updated = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
    serialize_oaps(oaps_updated, shortcode, mode="modified")


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("localhost")
    shortcode = "4123"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(
        retrieve_resources="specified_res_classes",
        specified_res_classes=["testonto:ImageThing"],
        retrieve_values="specified_props",
        specified_props=["knora-api:hasStillImageFileValue"],
    )

    update_aps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )
    update_doaps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )
    update_oaps(
        shortcode=shortcode,
        dsp_client=dsp_client,
        oap_config=oap_config,
    )


if __name__ == "__main__":
    main()
