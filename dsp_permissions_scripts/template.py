import copy

from dsp_permissions_scripts.ap.ap_delete import delete_ap_of_group_on_server
from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import apply_updated_aps_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.oap.oap_get import get_all_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
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
        if ap.forGroup == group.UNKNOWN_USER:
            if ApValue.ProjectAdminGroupAllPermission not in ap.hasPermissions:
                ap.add_permission(ApValue.ProjectAdminGroupAllPermission)
                modified_aps.append(ap)
    return modified_aps


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in copy.deepcopy(doaps):
        if doap.target.group == group.UNKNOWN_USER:
            doap.scope = PUBLIC
            modified_doaps.append(doap)
    return modified_doaps


def modify_oaps(oaps: list[Oap]) -> list[ResourceOap | ValueOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ResourceOap | ValueOap] = []
    for oap in copy.deepcopy(oaps):
        if oap.resource_oap:
            if group.SYSTEM_ADMIN not in oap.resource_oap.scope.CR:
                oap.resource_oap.scope = oap.resource_oap.scope.add("CR", group.SYSTEM_ADMIN)
                modified_oaps.append(oap.resource_oap)
        for value_oap in oap.value_oaps:
            if group.SYSTEM_ADMIN not in value_oap.scope.CR:
                value_oap.scope = value_oap.scope.add("CR", group.SYSTEM_ADMIN)
                modified_oaps.append(value_oap)
    return modified_oaps


def update_aps(host: str, shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    remaining_aps = delete_ap_of_group_on_server(
        host=host,
        existing_aps=project_aps,
        forGroup=group.UNKNOWN_USER,
        dsp_client=dsp_client,
    )
    modified_aps = modify_aps(remaining_aps)
    if not modified_aps:
        logger.info("There are no APs to update.")
        return
    apply_updated_aps_on_server(modified_aps, host, dsp_client)
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
    project_doaps_modified = modify_doaps(doaps=project_doaps)
    if not project_doaps_modified:
        logger.info("There are no DOAPs to update.")
        return
    apply_updated_doaps_on_server(project_doaps_modified, host, dsp_client)
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def update_oaps(host: str, shortcode: str, dsp_client: DspClient, oap_config: OapRetrieveConfig) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    oaps = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
    serialize_oaps(oaps, shortcode, mode="original")
    oaps_modified = modify_oaps(oaps)
    if not oaps_modified:
        logger.info("There are no OAPs to update.")
        return
    apply_updated_oaps_on_server(
        oaps=oaps_modified,
        host=host,
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
    host = Hosts.get_host("test")
    shortcode = "F18E"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(
        retrieve_resources="specified_res_classes",
        specified_res_classes=["my-data-model:ImageThing"],
        retrieve_values="specified_props",
        specified_props=["knora-api:hasStillImageFileValue"],
    )

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
    update_oaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
        oap_config=oap_config,
    )


if __name__ == "__main__":
    main()
