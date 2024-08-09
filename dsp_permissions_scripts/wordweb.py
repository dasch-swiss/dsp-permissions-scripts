import copy

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.oap.oap_get import get_all_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_oaps(oaps: list[Oap]) -> list[ResourceOap | ValueOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ResourceOap | ValueOap] = []
    for oap in copy.deepcopy(oaps):
        if oap.resource_oap:
            if group.UNKNOWN_USER not in oap.resource_oap.scope.V:
                oap.resource_oap.scope = oap.resource_oap.scope.add("V", group.UNKNOWN_USER)
                modified_oaps.append(oap.resource_oap)
        for value_oap in oap.value_oaps:
            if group.UNKNOWN_USER not in value_oap.scope.V:
                value_oap.scope = value_oap.scope.add("V", group.UNKNOWN_USER)
                modified_oaps.append(value_oap)
    return modified_oaps


def update_oaps(host: str, shortcode: str, dsp_client: DspClient, oap_config: OapRetrieveConfig) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    oaps = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
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


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("prod")
    shortcode = "0826"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(
        retrieve_resources="all",
        retrieve_values="all",
    )

    update_oaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
        oap_config=oap_config,
    )


if __name__ == "__main__":
    main()
