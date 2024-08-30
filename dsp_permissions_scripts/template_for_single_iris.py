from pathlib import Path

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import OPEN
from dsp_permissions_scripts.oap.update_iris import update_iris
from dsp_permissions_scripts.utils.authentication import login
from dsp_permissions_scripts.utils.get_logger import log_start_of_script


def main() -> None:
    """ """
    host = Hosts.get_host("rdu")
    shortcode = "0812"
    iri_file = Path("project_data/0812/iris_to_update.txt")
    new_scope = OPEN
    log_start_of_script(host, shortcode)
    dsp_client = login(host)

    update_iris(
        iri_file=iri_file,
        new_scope=new_scope,
        dsp_client=dsp_client,
    )


if __name__ == "__main__":
    main()
