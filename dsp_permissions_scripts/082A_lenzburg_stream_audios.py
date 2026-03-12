import copy

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import LIMITED_VIEW
from dsp_permissions_scripts.oap.oap_get import get_all_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import ModifiedOap
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_oaps(oaps: list[Oap]) -> list[ModifiedOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ModifiedOap] = []
    for oap in copy.deepcopy(oaps):
        new_oap = ModifiedOap()
        if oap.resource_oap.scope != LIMITED_VIEW:
            new_oap.resource_oap = oap.resource_oap.model_copy(update={"scope": LIMITED_VIEW})
        for value_oap in oap.value_oaps:
            if value_oap.scope != LIMITED_VIEW:
                new_oap.value_oaps.append(value_oap.model_copy(update={"scope": LIMITED_VIEW}))
        if not new_oap.is_empty():
            modified_oaps.append(new_oap)
    return modified_oaps


def update_oaps(shortcode: str, dsp_client: DspClient, oap_config: OapRetrieveConfig) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    oaps = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
    oaps_modified = modify_oaps(oaps)
    if not oaps_modified:
        logger.info("There are no OAPs to update.")
        return
    apply_updated_oaps_on_server(
        oaps=oaps_modified,
        shortcode=shortcode,
        dsp_client=dsp_client,
        nthreads=2,
    )


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.get_host("stage")
    shortcode = "082A"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(
        retrieve_resources="specified_res_classes",
        specified_res_classes=["sva:AudioRepresentation"],
        retrieve_values="all",
    )

    update_oaps(
        shortcode=shortcode,
        dsp_client=dsp_client,
        oap_config=oap_config,
    )


if __name__ == "__main__":
    main()
