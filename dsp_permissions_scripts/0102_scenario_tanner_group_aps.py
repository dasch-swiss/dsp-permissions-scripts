from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

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
    _ = create_new_ap_on_server(
        forGroup=CustomGroup(prefixed_iri="scenario-tanner:group-scenario-tanner"),
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


def main() -> None:
    host = Hosts.get_host("rdu")
    shortcode = "0102"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_aps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
