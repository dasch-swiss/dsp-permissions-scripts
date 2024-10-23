from dsp_permissions_scripts.doap.doap_delete import _delete_doap_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import NewEntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import OPEN
from dsp_permissions_scripts.models.scope import RESTRICTED_VIEW
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


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
        target=NewGroupDoapTarget(group=PROJECT_MEMBER),
        shortcode=shortcode,
        scope=OPEN,
        dsp_client=dsp_client,
    )
    restricted_class_name = "RestrictedAccessImage" if shortcode == "084C" else "ImageThing"
    restricted_class_iri = f"{dsp_client.server}/ontology/{shortcode}/testonto/v2#{restricted_class_name}"
    _ = create_new_doap_on_server(
        target=NewEntityDoapTarget(resource_class=restricted_class_iri),
        shortcode=shortcode,
        scope=RESTRICTED_VIEW,
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
    shortcode = "084C"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_doaps(
        shortcode=shortcode,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
