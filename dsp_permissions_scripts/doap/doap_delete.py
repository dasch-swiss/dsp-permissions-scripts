from urllib.parse import quote_plus

from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import Group
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _delete_doap_on_server(doap: Doap, dsp_client: DspClient) -> None:
    doap_iri = quote_plus(doap.doap_iri, safe="")
    try:
        dsp_client.delete(f"/admin/permissions/{doap_iri}")
    except ApiError as err:
        err.message = f"Could not delete DOAP {doap.doap_iri}"
        raise err from None


def delete_doap_of_group_on_server(
    host: str,
    existing_doaps: list[Doap],
    forGroup: Group,
    dsp_client: DspClient,
) -> list[Doap]:
    doaps_to_delete = [
        doap for doap in existing_doaps if isinstance(doap.target, GroupDoapTarget) and doap.target.group == forGroup
    ]
    if not doaps_to_delete:
        logger.warning(f"There are no DOAPs to delete on {host} for group {forGroup}")
        return existing_doaps
    logger.info(f"Deleting the DOAP for group {forGroup} on server {host}")
    for doap in doaps_to_delete:
        _delete_doap_on_server(doap, dsp_client)
        existing_doaps.remove(doap)
        logger.info(f"Deleted DOAP {doap.doap_iri}")
    return existing_doaps
