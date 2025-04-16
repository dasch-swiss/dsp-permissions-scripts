import copy

from dsp_permissions_scripts.doap.doap_delete import delete_doap_of_group_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import EntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_scopes_of_doaps_on_server
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import OPEN
from dsp_permissions_scripts.models.scope import RESTRICTED
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.get_logger import log_start_of_script

logger = get_logger(__name__)


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    restr_acc_img_iri = "http://www.knora.org/ontology/084C/church#RestrictedAccessImage"
    modified_doaps = []
    for doap in copy.deepcopy(doaps):
        if (
            isinstance(doap.target, EntityDoapTarget)
            and doap.target.resclass_iri == restr_acc_img_iri
            and doap.scope != RESTRICTED
        ):
            doap.scope = RESTRICTED
            modified_doaps.append(doap)
    return modified_doaps


def update_doaps(shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    if any(
        doap.target.group == group.PROJECT_MEMBER for doap in project_doaps if isinstance(doap.target, GroupDoapTarget)
    ) and not any(
        doap.target.group == group.KNOWN_USER for doap in project_doaps if isinstance(doap.target, GroupDoapTarget)
    ):
        remaining_doaps = delete_doap_of_group_on_server(
            existing_doaps=project_doaps,
            forGroup=group.PROJECT_MEMBER,
            dsp_client=dsp_client,
        )
        _ = create_new_doap_on_server(
            target=NewGroupDoapTarget(group=group.KNOWN_USER),
            shortcode=shortcode,
            scope=OPEN,
            dsp_client=dsp_client,
        )
    else:
        remaining_doaps = project_doaps
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
