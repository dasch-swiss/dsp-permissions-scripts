import warnings
from urllib.parse import quote_plus

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils import connection

logger = get_logger(__name__)


def _delete_ap_on_server(ap: Ap) -> None:
    ap_iri = quote_plus(ap.iri, safe="")
    connection.con.delete(f"/admin/permissions/{ap_iri}")


def delete_ap_of_group_on_server(
    host: str,
    existing_aps: list[Ap],
    forGroup: str,
) -> list[Ap]:
    aps_to_delete = [ap for ap in existing_aps if ap.forGroup == forGroup]
    if not aps_to_delete:
        logger.warning(f"There are no APs to delete on {host} for group {forGroup}")
        warnings.warn(f"There are no APs to delete on {host} for group {forGroup}")
        return existing_aps
    print(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    logger.info(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    for ap in aps_to_delete:
        _delete_ap_on_server(ap)
        existing_aps.remove(ap)
        logger.info(f"Deleted Administrative Permission {ap.iri} on host {host}")
    return existing_aps
