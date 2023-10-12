from dotenv import load_dotenv

from dsp_permissions_scripts.models import builtin_groups
from dsp_permissions_scripts.models.ap import Ap, ApValue
from dsp_permissions_scripts.models.doap import Doap
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.oap import Oap
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.utils.ap.ap_get import delete_ap, get_aps_of_project
from dsp_permissions_scripts.utils.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.doap_get import get_doaps_of_project
from dsp_permissions_scripts.utils.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.utils.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.utils.oap import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def modify_aps(aps: list[Ap]) -> list[Ap]:
    """Adapt this sample to your needs."""
    for ap in aps:
        if ap.forGroup == builtin_groups.PROJECT_ADMIN:
            if ApValue.ProjectAdminAllPermission not in ap.hasPermissions:
                ap.add_permission(ApValue.ProjectAdminAllPermission)
    return aps


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    for doap in doaps: 
        if doap.target.group in [builtin_groups.PROJECT_MEMBER, builtin_groups.PROJECT_ADMIN]:
            doap.scope = PUBLIC
    return doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Adapt this sample to your needs."""
    for oap in oaps:
        if builtin_groups.SYSTEM_ADMIN not in oap.scope.CR:
            oap.scope = oap.scope.add("CR", builtin_groups.SYSTEM_ADMIN)
    return oaps


def update_aps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """Sample function to modify the administrative permissions of a project."""
    project_aps = get_aps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_aps_of_project(
        project_aps=project_aps,
        shortcode=shortcode,
        mode="original",
    )
    remaining_aps = delete_ap(
        host=host,
        token=token,
        existing_aps=project_aps,
        forGroup=builtin_groups.PROJECT_MEMBER,
    )
    project_aps_updated = modify_aps(remaining_aps)
    serialize_aps_of_project(
        project_aps=project_aps_updated,
        shortcode=shortcode,
        mode="modified",
    )
    # apply_updated_aps_on_server(
    #     doaps=project_aps_updated,
    #     host=host,
    #     token=token,
    # )


def update_doaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
    )
    project_doaps_updated = modify_doaps(doaps=project_doaps)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
    )
    apply_updated_doaps_on_server(
        doaps=project_doaps_updated,
        host=host,
        token=token,
    )


def update_oaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    resource_oaps = get_all_resource_oaps_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    serialize_resource_oaps(
        resource_oaps=resource_oaps,
        shortcode=shortcode,
        mode="original",
    )
    resource_oaps_updated = modify_oaps(oaps=resource_oaps)
    serialize_resource_oaps(
        resource_oaps=resource_oaps_updated,
        shortcode=shortcode,
        mode="modified",
    )
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_updated,
        host=host,
        token=token,
        shortcode=shortcode,
    )


def main() -> None:
    """
    The main function provides you with 2 sample functions:
    one to update the Object Access Permissions of a project,
    and one to update the Default Object Access Permissions of a project.
    Both must first be adapted to your needs.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("test")
    shortcode = "F18E"
    token = login(host)

    update_aps(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    update_doaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    update_oaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )


if __name__ == "__main__":
    main()
