from dotenv import load_dotenv

from dsp_permissions_scripts.models.doap import Doap
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.oap import Oap
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.doap_get import get_doaps_of_project
from dsp_permissions_scripts.utils.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.utils.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.utils.oap import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.utils.project import get_all_resource_oaps_of_project


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    for doap in doaps: 
        if doap.target.group in [BuiltinGroup.PROJECT_MEMBER, BuiltinGroup.PROJECT_ADMIN]:
            doap.scope = PUBLIC
    return doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Adapt this sample to your needs."""
    for oap in oaps:
        if BuiltinGroup.SYSTEM_ADMIN.value not in oap.scope.CR:
            oap.scope = oap.scope.add("CR", BuiltinGroup.SYSTEM_ADMIN)
    return oaps


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
