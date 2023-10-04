from dotenv import load_dotenv

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.permissions import (
    get_doaps_of_project,
    print_doaps_of_project,
    set_doaps_of_groups,
    update_permissions_for_resources_and_values,
)
from dsp_permissions_scripts.utils.project import get_all_resource_iris_of_project


def main() -> None:
    """
    The main method assembles a sample call of all available high-level functions.
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    host = Hosts.get_host("localhost")
    shortcode = "4123"
    token = login(host)

    new_scope = PUBLIC
    groups = [BuiltinGroup.PROJECT_ADMIN, BuiltinGroup.PROJECT_MEMBER]

    doaps = get_doaps_of_project(
        host=host,
        shortcode=shortcode,
        token=token,
    )
    print_doaps_of_project(
        doaps=doaps,
        host=host,
        shortcode=shortcode,
    )
    set_doaps_of_groups(
        scope=new_scope,
        groups=groups,
        host=host,
        shortcode=shortcode,
        token=token,
    )
    resource_iris = get_all_resource_iris_of_project(
        shortcode=shortcode,
        host=host,
        token=token,
    )
    update_permissions_for_resources_and_values(
        resource_iris=resource_iris,
        scope=new_scope,
        host=host,
        token=token,
    )


if __name__ == "__main__":
    main()
