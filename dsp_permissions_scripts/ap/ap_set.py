from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.ap.ap_get import create_admin_route_object_from_ap
from dsp_permissions_scripts.ap.ap_get import create_ap_from_admin_route_object
from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import GroupType
from dsp_permissions_scripts.models.group import get_full_iri_from_prefixed_iri
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_and_onto_iris_by_shortcode

logger = get_logger(__name__)


def _update_ap_scope_on_server(ap: Ap, dsp_client: DspClient) -> Ap:
    iri = quote_plus(ap.iri, safe="")
    payload = {"hasPermissions": create_admin_route_object_from_ap(ap)["hasPermissions"]}
    try:
        response = dsp_client.put(f"/admin/permissions/{iri}/hasPermissions", data=payload)
    except ApiError as err:
        err.message = f"Could not update scope of Administrative Permission {ap.iri}"
        raise err from None
    ap_updated: dict[str, Any] = response["administrative_permission"]
    ap_object_updated = create_ap_from_admin_route_object(ap_updated, dsp_client)
    return ap_object_updated


def apply_updated_scopes_of_aps_on_server(aps: list[Ap], dsp_client: DspClient) -> None:
    if not aps:
        logger.warning(f"There are no APs to update on {dsp_client.server}")
        return
    logger.info(f"****** Updating scopes of {len(aps)} Administrative Permissions on {dsp_client.server}... ******")
    for ap in aps:
        try:
            _ = _update_ap_scope_on_server(ap, dsp_client)
            logger.info(f"Successfully updated AP {ap.iri}")
        except ApiError as err:
            logger.error(err)
    logger.info(f"Finished updating scopes of {len(aps)} Administrative Permissions on {dsp_client.server}")


def create_new_ap_on_server(
    forGroup: GroupType,
    shortcode: str,
    hasPermissions: list[ApValue],
    dsp_client: DspClient,
) -> Ap | None:
    proj_iri, _ = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    payload = {
        "forGroup": get_full_iri_from_prefixed_iri(forGroup.prefixed_iri, dsp_client),
        "forProject": proj_iri,
        "hasPermissions": [
            {"additionalInformation": None, "name": ap_val.value, "permissionCode": None} for ap_val in hasPermissions
        ],
    }
    try:
        response = dsp_client.post("/admin/permissions/ap", data=payload)
        logger.info(f"Successfully created new AP for group {forGroup.prefixed_iri}")
        return create_ap_from_admin_route_object(response["administrative_permission"], dsp_client)
    except ApiError:
        logger.error(f"Could not create new AP for group {forGroup}")
        return None
