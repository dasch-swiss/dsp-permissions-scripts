from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import get_value_oaps
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_resource
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_value
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger
from dsp_permissions_scripts.utils.helpers import KNORA_ADMIN_ONTO_NAMESPACE

logger = get_logger(__name__)


@dataclass
class IRIUpdater(ABC):
    iri: str
    dsp_client: DspClient
    err_msg: str | None = field(init=False, default=None)

    @abstractmethod
    def update_iri(self, new_scope: PermissionScope) -> None:
        pass

    @staticmethod
    def from_string(string: str, dsp_client: DspClient) -> ResourceIRIUpdater | ValueIRIUpdater:
        if re.search(r"^http://rdfh\.ch/[^/]{4}/[^/]{22}/values/[^/]{22}$", string):
            return ValueIRIUpdater(string, dsp_client)
        elif re.search(r"^http://rdfh\.ch/[^/]{4}/[^/]{22}$", string):
            return ResourceIRIUpdater(string, dsp_client)
        else:
            raise InvalidIRIError(f"Could not parse IRI {string}")

    def _get_res_dict(self, res_iri: str) -> dict[str, Any]:
        return self.dsp_client.get(f"/v2/resources/{quote_plus(res_iri, safe='')}")


@dataclass
class ResourceIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope) -> None:
        res_dict = self._get_res_dict(self.iri)
        try:
            update_permissions_for_resource(
                resource_iri=self.iri,
                lmd=res_dict["knora-api:lastModificationDate"],
                resource_type=res_dict["@type"],
                context=res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                scope=new_scope,
                dsp_client=self.dsp_client,
            )
        except ApiError as err:
            self.err_msg = err.message
            logger.error(self.err_msg)


@dataclass
class ValueIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope) -> None:
        res_iri = re.sub(r"/values/[^/]{22}$", "", self.iri)
        res_dict = self._get_res_dict(res_iri)
        val_oap = next((v for v in get_value_oaps(res_dict) if v.value_iri == self.iri), None)
        if not val_oap:
            self.err_msg = f"Could not find value {self.iri} in resource {res_dict['@id']}"
            logger.error(self.err_msg)
            return
        val_oap.scope = new_scope
        try:
            update_permissions_for_value(
                value=val_oap,
                resource_type=res_dict["@type"],
                context=res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                dsp_client=self.dsp_client,
            )
        except ApiError as err:
            self.err_msg = err.message
            logger.error(self.err_msg)


def update_iris(
    iri_file: Path,
    new_scope: PermissionScope,
    dsp_client: DspClient,
) -> None:
    iri_updaters = _initialize_iri_updaters(iri_file, dsp_client)
    for iri in iri_updaters:
        iri.update_iri(new_scope)
    _tidy_up(iri_updaters, iri_file)


def _initialize_iri_updaters(iri_file: Path, dsp_client: DspClient) -> list[ResourceIRIUpdater | ValueIRIUpdater]:
    logger.info(f"Read IRIs from file {iri_file} and initialize IRI updaters...")
    iris_raw = {x for x in iri_file.read_text().splitlines() if re.search(r"\w", x)}
    iri_updaters = [IRIUpdater.from_string(iri, dsp_client) for iri in iris_raw]
    res_counter = sum(isinstance(x, ResourceIRIUpdater) for x in iri_updaters)
    val_counter = sum(isinstance(x, ValueIRIUpdater) for x in iri_updaters)
    logger.info(
        f"Perform {len(iri_updaters)} updates ({res_counter} resources and {val_counter} values) "
        f"on server {dsp_client.server}..."
    )
    return iri_updaters


def _tidy_up(iri_updaters: list[ResourceIRIUpdater | ValueIRIUpdater], iri_file: Path) -> None:
    if failed_updaters := [x for x in iri_updaters if x.err_msg]:
        failed_iris_file = iri_file.with_stem(f"{iri_file.stem}_failed")
        failed_iris_file.write_text("\n".join([f"{x.iri}\t\t{x.err_msg}" for x in failed_updaters]))
        logger.info(f"Some updates failed. The failed IRIs and error messages have been saved to {failed_iris_file}.")
    else:
        logger.info(f"All {len(iri_updaters)} updates were successful.")
