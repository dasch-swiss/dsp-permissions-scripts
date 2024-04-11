from dsp_permissions_scripts.doap.doap_get import get_doaps_of_project
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_set import apply_updated_doaps_on_server
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.oap.oap_get import get_all_resource_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import log_start_of_script


def modify_doaps(doaps: list[Doap]) -> list[Doap]:
    """Adapt this sample to your needs."""
    modified_doaps = []
    for doap in doaps:
        doap.scope = doap.scope.add("RV", group.UNKNOWN_USER)
        doap.scope = doap.scope.add("RV", group.KNOWN_USER)
        modified_doaps.append(doap)
    return modified_doaps


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    """Adapt this sample to your needs."""
    modified_oaps = []
    for oap in oaps:
        for user in [group.UNKNOWN_USER, group.KNOWN_USER]:
            oap.scope = oap.scope.remove("V", user) if user in oap.scope.V else oap.scope
            oap.scope = oap.scope.add("RV", user) if user not in oap.scope.RV else oap.scope
        modified_oaps.append(oap)
    return modified_oaps


def update_doaps(host: str, shortcode: str, dsp_client: DspClient) -> None:
    """Sample function to modify the Default Object Access Permissions of a project."""
    project_doaps = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps,
        shortcode=shortcode,
        mode="original",
        host=host,
    )
    project_doaps_modified = modify_doaps(doaps=project_doaps)
    apply_updated_doaps_on_server(project_doaps_modified, host, dsp_client)
    project_doaps_updated = get_doaps_of_project(shortcode, dsp_client)
    serialize_doaps_of_project(
        project_doaps=project_doaps_updated,
        shortcode=shortcode,
        mode="modified",
        host=host,
    )


def update_oaps(host: str, shortcode: str, dsp_client: DspClient, context: dict[str, str] | None = None) -> None:
    """Sample function to modify the Object Access Permissions of a project."""
    context = context or {}
    excluded = [f"{context["fotoarchivkunsthalle"]}Exhibitions"]
    resource_oaps = get_all_resource_oaps_of_project(shortcode, dsp_client, excluded_class_iris=excluded)
    serialize_resource_oaps(resource_oaps, shortcode, mode="original")
    resource_oaps_modified = modify_oaps(oaps=resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_modified,
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
        nthreads=4,
    )
    resource_oaps_updated = get_all_resource_oaps_of_project(shortcode, dsp_client)
    serialize_resource_oaps(resource_oaps_updated, shortcode, mode="modified")


def main() -> None:
    """
    The main function provides you with 3 sample functions:
    One to update the Administrative Permissions of a project,
    one to update the Default Object Access Permissions of a project,
    and one to update the Object Access Permissions of a project.
    All must first be adapted to your needs.
    """
    host = Hosts.STAGE
    shortcode = "080C"
    log_start_of_script(host, shortcode)
    dsp_client = login(host)
    context = {"fotoarchivkunsthalle": f"{host.replace("https:", "http:")}/ontology/080C/fotoarchivkunsthalle/v2#"}

    update_doaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
    )
    update_oaps(
        host=host,
        shortcode=shortcode,
        dsp_client=dsp_client,
        context=context,
    )


if __name__ == "__main__":
    main()