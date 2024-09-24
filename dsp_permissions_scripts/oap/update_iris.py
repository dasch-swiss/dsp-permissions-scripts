from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import get_value_oaps
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_resource
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_value
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceIri:
    iri: str


@dataclass
class ValueIri:
    iri: str


@dataclass
class IriUpdateProblem:
    iri: ResourceIri | ValueIri
    err_msg: str


def update_iris(
    iri_file: Path,
    new_scope: PermissionScope,
    dsp_client: DspClient,
) -> None:
    iris = _get_iris_from_file(iri_file, dsp_client)
    problems: list[IriUpdateProblem] = []
    for iri in iris:
        if isinstance(iri, ResourceIri) and (prob := _update_res_iri(iri, new_scope, dsp_client)):
            problems.append(prob)
        elif isinstance(iri, ValueIri) and (prob := _update_val_iri(iri, new_scope, dsp_client)):
            problems.append(prob)
    _tidy_up(problems, iri_file)


def _get_iris_from_file(iri_file: Path, dsp_client: DspClient) -> list[ResourceIri | ValueIri]:
    logger.info(f"Read IRIs from file {iri_file} and initialize IRI updaters...")
    iris_raw = {x for x in iri_file.read_text().splitlines() if re.search(r"\w", x)}
    iris = [_get_iri_wrapper(iri) for iri in iris_raw]
    res_counter = sum(isinstance(x, ResourceIri) for x in iris)
    val_counter = sum(isinstance(x, ValueIri) for x in iris)
    logger.info(
        f"Perform {len(iris)} updates ({res_counter} resources and {val_counter} values) "
        f"on server {dsp_client.server}..."
    )
    return iris


def _get_iri_wrapper(string: str) -> ResourceIri | ValueIri:
    if re.search(r"^http://rdfh\.ch/[^/]{4}/[^/]{22}/values/[^/]{22}$", string):
        return ValueIri(string)
    elif re.search(r"^http://rdfh\.ch/[^/]{4}/[^/]{22}$", string):
        return ResourceIri(string)
    else:
        raise InvalidIRIError(f"Could not parse IRI {string}")


def _update_res_iri(iri: ResourceIri, new_scope: PermissionScope, dsp_client: DspClient) -> IriUpdateProblem | None:
    res_dict = _get_res_dict(dsp_client, iri)
    try:
        update_permissions_for_resource(
            resource_iri=iri.iri,
            lmd=res_dict["knora-api:lastModificationDate"],
            resource_type=res_dict["@type"],
            context=res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
            scope=new_scope,
            dsp_client=dsp_client,
        )
        return None
    except ApiError as err:
        problem = IriUpdateProblem(iri, err.message)
        logger.error(problem.err_msg)
        return problem


def _update_val_iri(iri: ValueIri, new_scope: PermissionScope, dsp_client: DspClient) -> IriUpdateProblem | None:
    res_dict = _get_res_dict(dsp_client, iri)
    val_oap = next((v for v in get_value_oaps(res_dict) if v.value_iri == iri.iri), None)
    if not val_oap:
        problem = IriUpdateProblem(iri, f"Could not find value {iri} in resource {res_dict['@id']}")
        logger.error(problem.err_msg)
        return problem
    val_oap.scope = new_scope
    try:
        update_permissions_for_value(
            value=val_oap,
            resource_type=res_dict["@type"],
            context=res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
            dsp_client=dsp_client,
        )
        return None
    except ApiError as err:
        problem = IriUpdateProblem(iri, err.message)
        logger.error(problem.err_msg)
        return problem


def _get_res_dict(dsp_client: DspClient, iri: ResourceIri | ValueIri) -> dict[str, Any]:
    res_iri = re.sub(r"/values/[^/]{22}$", "", iri.iri)
    return dsp_client.get(f"/v2/resources/{quote_plus(res_iri, safe='')}")


def _tidy_up(problems: list[IriUpdateProblem], iri_file: Path) -> None:
    if problems:
        failed_iris_file = iri_file.with_stem(f"{iri_file.stem}_failed")
        failed_iris_file.write_text("\n".join([f"{x.iri}\t\t{x.err_msg}" for x in problems]))
        logger.info(f"{len(problems)} updates failed. The failed IRIs have been saved to {failed_iris_file}.")
    else:
        logger.info("All updates were successful.")
