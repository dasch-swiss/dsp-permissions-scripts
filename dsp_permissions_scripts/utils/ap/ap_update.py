from dsp_permissions_scripts.models.ap import Ap, ApValue
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.utils.ap.ap import delete_ap, get_aps_of_project


def modify_aps(aps: list[Ap]) -> list[Ap]:
    """Adapt this sample to your needs."""
    for ap in aps:
        if ap.forGroup == BuiltinGroup.PROJECT_ADMIN.value:
            if ApValue.ProjectAdminAllPermission not in ap.hasPermissions:
                ap.add_permission(ApValue.ProjectAdminAllPermission)
    return aps


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
    # serialize_aps_of_project(
    #     project_aps=project_aps,
    #     shortcode=shortcode,
    #     mode="original",
    # )
    project_aps_updated = modify_aps(project_aps)
    delete_ap(
        host=host,
        token=token,
        existing_aps=project_aps,
        forGroup=BuiltinGroup.PROJECT_MEMBER,
    )
    # serialize_aps_of_project(
    #     project_doaps=project_aps_updated,
    #     shortcode=shortcode,
    #     mode="modified",
    # )
    # apply_updated_aps_on_server(
    #     doaps=project_aps_updated,
    #     host=host,
    #     token=token,
    # )
