import copy

from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_scopes_of_doaps_on_server
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import RESTRICTED_VIEW
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


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in copy.deepcopy(doaps):
        if doap.scope != RESTRICTED_VIEW:
            doap.scope = RESTRICTED_VIEW
            modified_doaps.append(doap)
    return modified_doaps


def modify_oaps(oaps: list[Oap]) -> list[ModifiedOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ModifiedOap] = []
    for oap in copy.deepcopy(oaps):
        new_oap = ModifiedOap()
        if oap.resource_oap.scope != RESTRICTED_VIEW:
            new_oap.resource_oap = oap.resource_oap.model_copy(update={"scope": RESTRICTED_VIEW})
        for value_oap in oap.value_oaps:
            if value_oap.scope != RESTRICTED_VIEW:
                new_oap.value_oaps.append(value_oap.model_copy(update={"scope": RESTRICTED_VIEW}))
        if not new_oap.is_empty():
            modified_oaps.append(new_oap)
    return modified_oaps


def update_doaps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    project_doaps_modified = modify_doaps(doaps=project_doaps)
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


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("rdu")
    shortcode = "080C"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)
    oap_config = OapRetrieveConfig(retrieve_resources="all", retrieve_values="all")

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
