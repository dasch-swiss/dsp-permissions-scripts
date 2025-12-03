from pathlib import Path

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PUBLIC
from dsp_permissions_scripts.oap.update_iris import update_iris
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.get_logger import log_start_of_script


def main() -> None:
    """
    Use this script if you want to update the OAPs of resources/values provided in a text file.
    The text file should contain the IRIs of the resources/values (one per line) to update.
    Resource IRIs and value IRIs can be mixed in the text file.
    """
    host = Hosts.get_host("localhost")
    shortcode = "4123"
    iri_file = Path("project_data/4123/iris_to_update.txt")
    new_scope = PUBLIC
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_iris(
        iri_file=iri_file,
        new_scope=new_scope,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
