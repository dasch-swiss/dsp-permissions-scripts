from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import EntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_scopes_of_doaps_on_server
from dsp_permissions_scripts.models.group import PROJECT_MEMBER
from dsp_permissions_scripts.models.group import CustomGroup
from dsp_permissions_scripts.models.host import Hosts
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


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    tanner_group = CustomGroup(prefixed_iri="scenario-tanner:group-scenario-tanner")
    for doap in doaps:
        is_proj_adm_doap = bool(
            isinstance(doap.target, GroupDoapTarget)
            and doap.target.group == PROJECT_MEMBER
            and tanner_group not in doap.scope.M
        )
        is_interview_doap = bool(
            isinstance(doap.target, EntityDoapTarget)
            and str(doap.target.resclass_iri).endswith("Interview")
            and tanner_group not in doap.scope.M
        )
        if is_proj_adm_doap or is_interview_doap:
            doap.scope = doap.scope.add(permission="M", group=tanner_group)
    return doaps


def modify_oaps(oaps: list[Oap]) -> list[ModifiedOap]:
    """Adapt this sample to your needs."""
    modified_oaps: list[ModifiedOap] = []
    # shortened IRI doesn't seem to work as expected, so we use the full IRI
    tanner_group = CustomGroup(prefixed_iri="http://rdfh.ch/groups/0102/oe8-uWCgS4Wl6wfOvaFGCA")
    for oap in oaps:
        new_oap = ModifiedOap()
        if tanner_group not in oap.resource_oap.scope.M:
            new_scope = oap.resource_oap.scope.add(permission="M", group=tanner_group)
            new_oap.resource_oap = oap.resource_oap.model_copy(update={"scope": new_scope})
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
    host = Hosts.get_host("prod")
    shortcode = "0102"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(retrieve_resources="all", retrieve_values="none")

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
