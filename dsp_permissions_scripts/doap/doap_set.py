from urllib.parse import quote_plus

from dsp_permissions_scripts.doap.doap_get import create_doap_from_admin_route_response
from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import NewEntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewGroupDoapTarget
from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.project import get_project_iri_and_onto_iris_by_shortcode
from dsp_permissions_scripts.utils.scope_serialization import create_admin_route_object_from_scope

logger = get_logger(__name__)


def _update_doap_scope_on_server(doap_iri: str, scope: PermissionScope, dsp_client: DspClient) -> Doap:
    iri = quote_plus(doap_iri, safe="")
    payload = {"hasPermissions": create_admin_route_object_from_scope(scope)}
    try:
        response = dsp_client.put(f"/admin/permissions/{iri}/hasPermissions", data=payload)
    except ApiError as err:
        err.message = f"Could not update scope of DOAP {doap_iri}"
        raise err from None
    new_doap = create_doap_from_admin_route_response(response["default_object_access_permission"])
    return new_doap


def apply_updated_scopes_of_doaps_on_server(doaps: list[Doap], host: str, dsp_client: DspClient) -> None:
    if not doaps:
        logger.warning(f"There are no DOAPs to update on {host}")
        return
    logger.info(f"****** Updating scopes of {len(doaps)} DOAPs on {host}... ******")
    for d in doaps:
        try:
            _ = _update_doap_scope_on_server(d.doap_iri, d.scope, dsp_client)
            logger.info(f"Successfully updated DOAP {d.doap_iri}")
        except ApiError as err:
            logger.error(err)
    logger.info(f"Finished updating scopes of {len(doaps)} DOAPs on {host}")


def create_new_doap_on_server(
    target: NewGroupDoapTarget | NewEntityDoapTarget,
    shortcode: str,
    scope: PermissionScope,
    dsp_client: DspClient,
) -> Doap | None:
    proj_iri, _ = get_project_iri_and_onto_iris_by_shortcode(shortcode, dsp_client)
    payload = {
        "forGroup": target.group.full_iri() if isinstance(target, NewGroupDoapTarget) else None,
        "forProject": proj_iri,
        "forProperty": target.property if isinstance(target, NewEntityDoapTarget) else None,
        "forResourceClass": target.resource_class if isinstance(target, NewEntityDoapTarget) else None,
        "hasPermissions": create_admin_route_object_from_scope(scope),
    }
    try:
        response = dsp_client.post("/admin/permissions/doap", data=payload)
        logger.info(f"Successfully created new DOAP for target {target}")
        return create_doap_from_admin_route_response(response["default_object_access_permission"])
    except ApiError:
        logger.error(f"Could not create new DOAP for target {target}")
        return None
