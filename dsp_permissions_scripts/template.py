from dotenv import load_dotenv

from dsp_permissions_scripts.ap.ap_delete import delete_ap_of_group_on_server
from dsp_permissions_scripts.ap.ap_get import get_aps_of_project
from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.ap.ap_set import apply_updated_aps_on_server
from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.models import builtin_groups
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.oap.oap_get import get_all_resource_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils import dsp_client
from dsp_permissions_scripts.utils.authentication import get_login_credentials


def modify_aps(aps: list[Ap]) -> list[Ap]:
    """Adapt this sample to your needs."""
    modified_aps = []
    for ap in aps:
        if ap.forGroup == builtin_groups.UNKNOWN_USER:
            if ApValue.ProjectAdminGroupAllPermission not in ap.hasPermissions:
                ap.add_permission(ApValue.ProjectAdminGroupAllPermission)
                modified_aps.append(ap)
    return modified_aps


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in doaps:
        if doap.target.group == builtin_groups.UNKNOWN_USER:
            doap.scope = PUBLIC
            modified_doaps.append(doap)
    return modified_doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Adapt this sample to your needs."""
    modified_oaps = []
    for oap in oaps:
        if builtin_groups.SYSTEM_ADMIN not in oap.scope.CR:
            oap.scope = oap.scope.add("CR", builtin_groups.SYSTEM_ADMIN)
            modified_oaps.append(oap)
    return modified_oaps


def update_aps(
    host: str,
    shortcode: str,
) -> None:
    """Sample function to modify the Administrative Permissions of a project."""
    project_aps = get_aps_of_project(
        host=host,
        shortcode=shortcode,
    )
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    remaining_aps = delete_ap_of_group_on_server(
        host=host,
        existing_aps=project_aps,
        forGroup=builtin_groups.UNKNOWN_USER,
    )
    modified_aps = modify_aps(remaining_aps)
    apply_updated_aps_on_server(
        aps=modified_aps,
        host=host,
    )
    project_aps_updated = get_aps_of_project(
        host=host,
        shortcode=shortcode,
    )
    serialize_aps_of_project(
        project_aps=project_aps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def update_doaps(
    host: str,
    shortcode: str,
) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
    )
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    project_doaps_modified = modify_doaps(doaps=project_doaps)
    apply_updated_doaps_on_server(
        doaps=project_doaps_modified,
        host=host,
    )
    project_doaps_updated = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
    )
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def update_oaps(
    host: str,
    shortcode: str,
) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    resource_oaps = get_all_resource_oaps_of_project(shortcode)
    serialize_resource_oaps(
        resource_oaps=resource_oaps,
        shortcode=shortcode,
        mode="original",
    )
    resource_oaps_modified = modify_oaps(oaps=resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_modified,
        host=host,
        shortcode=shortcode,
        nthreads=4,
    )
    resource_oaps_updated = get_all_resource_oaps_of_project(shortcode)
    serialize_resource_oaps(
        resource_oaps=resource_oaps_updated,
        shortcode=shortcode,
        mode="modified",
    )


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("test")
    shortcode = "F18E"
    user, pw = get_login_credentials(host)  # read login credentials from environment variables
    dsp_client.dspClient = dsp_client.DspClient(host)
    dsp_client.dspClient.login(user, pw)

    update_aps(
        host=host,
        shortcode=shortcode,
    )
    update_doaps(
        host=host,
        shortcode=shortcode,
    )
    update_oaps(
        host=host,
        shortcode=shortcode,
    )


if __name__ == "__main__":
    main()
