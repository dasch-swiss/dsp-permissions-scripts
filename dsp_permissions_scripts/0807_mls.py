import copy

from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import apply_updated_scopes_of_aps_on_server
from dsp_permissions_scripts.ap.ap_set import create_new_ap_on_server
from dsp_permissions_scripts.doap.doap_delete import delete_doap_of_group_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import create_new_doap_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
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
    project_aps = get_aps_of_project(shortcode, dsp_client)
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    for ap in project_aps:
        if ap.forGroup == group.PROJECT_ADMIN:
            ap.add_permission(ApValue.ProjectAdminAllPermission)
    apply_updated_scopes_of_aps_on_server(project_aps, dsp_client)
    create_new_ap_on_server(
        forGroup=group.PROJECT_MEMBER,
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


def update_doaps(shortcode: str, dsp_client: DspClient) -> None:
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        server=dsp_client.server,
    )
    delete_doap_of_group_on_server(existing_doaps=project_doaps, forGroup=group.PROJECT_ADMIN, dsp_client=dsp_client)
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.PROJECT_ADMIN),
        shortcode=shortcode,
        scope=PUBLIC,
        dsp_client=dsp_client,
    )
    _ = create_new_doap_on_server(
        target=NewGroupDoapTarget(group=group.PROJECT_MEMBER),
        shortcode=shortcode,
        scope=PUBLIC,
        dsp_client=dsp_client,
    )
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        server=dsp_client.server,
    )


def modify_oaps(oaps: list[Oap]) -> list[ModifiedOap]:
    modified_oaps: list[ModifiedOap] = []
    for oap in copy.deepcopy(oaps):
        new_oap = ModifiedOap()
        new_oap.resource_oap = oap.resource_oap.model_copy(update={"scope": PUBLIC})
        for value_oap in oap.value_oaps:
            new_oap.value_oaps.append(value_oap.model_copy(update={"scope": PUBLIC}))
        modified_oaps.append(new_oap)
    return modified_oaps


def update_oaps(shortcode: str, dsp_client: DspClient, oap_config: OapRetrieveConfig) -> None:
    oaps = get_all_oaps_of_project(shortcode, dsp_client, oap_config)
    oaps_modified = modify_oaps(oaps)
    apply_updated_oaps_on_server(
        oaps=oaps_modified,
        shortcode=shortcode,
        dsp_client=dsp_client,
        nthreads=4,
    )


def main() -> None:
    host = Hosts.get_host("rdu")
    shortcode = "0807"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    oap_config = OapRetrieveConfig(retrieve_resources="all", retrieve_values="all")

    update_aps(shortcode=shortcode, dsp_client=dsp_client)
    update_doaps(shortcode=shortcode, dsp_client=dsp_client)
    update_oaps(shortcode=shortcode, dsp_client=dsp_client, oap_config=oap_config)


if __name__ == "__main__":
    main()
