import copy

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import DSP_TOOLS_STASHED
from dsp_permissions_scripts.models.scope import WEBERN_INTENDED
from dsp_permissions_scripts.oap.oap_get import get_all_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_serialize import serialize_oaps
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

# pylint: disable=R0801 # Similar lines in 2 files


logger = get_logger(__name__)


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Adapt this sample to your needs."""
    modified_oaps = []
    for oap in copy.deepcopy(oaps):
        modified = False
        for value_oap in oap.value_oaps:
            if value_oap.scope == DSP_TOOLS_STASHED:
                value_oap.scope = WEBERN_INTENDED
                modified = True
        if modified:
            modified_oaps.append(oap)
    return modified_oaps


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
    host = Hosts.get_host("stage")
    shortcode = "0806"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    prefix = "webern-onto"
    resclasses = [f"{prefix}:{x}" for x in ["Correspondence", "MusicalPiece", "Opus", "Bibliography"]]
    props = [
        f"{prefix}:{x}"
        for x in [
            "hasCorrespAdresseeValue",
            "hasCorrespSenderValue",
            "hasCorrespContributorValue",
            "hasPerformanceValue",
            "hasMovementValue",
            "hasBiblTitleIndependentRefValue",
        ]
    ]
    oap_config = OapRetrieveConfig(
        retrieve_resources="specified_res_classes",
        specified_res_classes=resclasses,
        retrieve_values="specified_props",
        specified_props=props,
    )

    update_oaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
        oap_config=oap_config,
    )


if __name__ == "__main__":
    main()
