# pylint: disable=duplicate-code

from dotenv import load_dotenv

from dsp_permissions_scripts.models import builtin_groups
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.oap.oap_get import get_all_resource_oaps_of_project
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_serialize import serialize_resource_oaps
from dsp_permissions_scripts.oap.oap_set import apply_updated_oaps_on_server
from dsp_permissions_scripts.utils.authentication import login


def modify_oaps(oaps: list[Oap]) -> list[Oap]:
    for oap in oaps:
        oap.scope = oap.scope.remove("V", builtin_groups.KNOWN_USER)
        oap.scope = oap.scope.remove("V", builtin_groups.UNKNOWN_USER)
        oap.scope = oap.scope.add("RV", builtin_groups.KNOWN_USER)
        oap.scope = oap.scope.add("RV", builtin_groups.UNKNOWN_USER)
    return oaps


def update_oaps(
    host: str,
    shortcode: str,
    token: str,
) -> None:
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
    resource_oaps_modified = modify_oaps(oaps=resource_oaps)
    apply_updated_oaps_on_server(
        resource_oaps=resource_oaps_modified,
        host=host,
        token=token,
        shortcode=shortcode,
    )
    resource_oaps_updated = get_all_resource_oaps_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    serialize_resource_oaps(
        resource_oaps=resource_oaps_updated,
        shortcode=shortcode,
        mode="modified",
    )


def modify_postcards() -> None:
    """Adapt the project "Postkarten Russlands" on prod: Set all images to restricted."""
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("stage")
    shortcode = "0811"
    token = login(host)

    update_oaps(
        host=host,
        shortcode=shortcode,
        token=token,
    )


if __name__ == "__main__":
    modify_postcards()
