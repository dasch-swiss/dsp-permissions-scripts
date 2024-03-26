from urllib.parse import quote_plus

import requests

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.models.api_error import ApiError
from dsp_permissions_scripts.utils.authentication import get_protocol
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.try_request import http_call_with_retry

logger = get_logger(__name__)


def _delete_ap_on_server(
    ap: Ap,
    host: str,
    token: str,
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    ap_iri = quote_plus(ap.iri, safe="")
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/admin/permissions/{ap_iri}"
    response = http_call_with_retry(
        action=lambda: requests.delete(url, headers=headers, timeout=20),
        err_msg=f"Could not delete Administrative Permission {ap.iri}",
    )
    if response.status_code != 200:
        raise ApiError(f"Could not delete Administrative Permission {ap.iri}", response.text, response.status_code)


def delete_ap_of_group_on_server(
    host: str,
    token: str,
    existing_aps: list[Ap],
    forGroup: str,
) -> list[Ap]:
    aps_to_delete = [ap for ap in existing_aps if ap.forGroup == forGroup]
    if not aps_to_delete:
        logger.warning(f"There are no APs to delete on {host} for group {forGroup}")
        return existing_aps
    logger.info(f"Deleting the Administrative Permissions for group {forGroup} on server {host}")
    for ap in aps_to_delete:
        _delete_ap_on_server(
            ap=ap,
            host=host,
            token=token,
        )
        existing_aps.remove(ap)
        logger.info(f"Deleted Administrative Permission {ap.iri}")
    return existing_aps
