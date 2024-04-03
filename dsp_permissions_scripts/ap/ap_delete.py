from urllib.parse import quote_plus

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _delete_ap_on_server(ap: Ap, dsp_client: DspClient) -> None:
    ap_iri = quote_plus(ap.iri, safe="")
    try:
        dsp_client.delete(f"/admin/permissions/{ap_iri}")
    except ApiError as err:
        err.message = f"Could not delete Administrative Permission {ap.iri}"
        raise err from None


def delete_ap_of_group_on_server(
    host: str,
    existing_aps: list[Ap],
    forGroup: Group,
    dsp_client: DspClient,
) -> list[Ap]:
    aps_to_delete = [ap for ap in existing_aps if ap.forGroup == forGroup]
    if not aps_to_delete:
        logger.warning(f"There are no APs to delete on {host} for group {forGroup}")
        return existing_aps
    logger.info(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    for ap in aps_to_delete:
        _delete_ap_on_server(ap, dsp_client)
        existing_aps.remove(ap)
        logger.info(f"Deleted Administrative Permission {ap.iri}")
    return existing_aps
