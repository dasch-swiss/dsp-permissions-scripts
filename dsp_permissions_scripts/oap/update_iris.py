from __future__ import annotations

import re
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import get_value_oaps
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_resource
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_value
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


@dataclass
class IRIUpdater(metaclass=ABCMeta):
    iri: str
    res_dict: dict[str, Any]
    err_msg: str | None = field(init=False, default=None)

    @abstractmethod
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        pass

    @staticmethod
    def from_string(string: str, dsp_client: DspClient) -> ResourceIRIUpdater | ValueIRIUpdater:
        res_iri = re.sub(r"/values/[^/]+$", "", string)
        res_dict = dsp_client.get(f"/v2/resources/{quote_plus(res_iri, safe='')}")
        if re.search(r"http://rdfh\.ch/[^/]{4}/[^/]+/values/[^/]+", string):
            return ValueIRIUpdater(string, res_dict)
        return ResourceIRIUpdater(string, res_dict)


@dataclass
class ResourceIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        try:
            update_permissions_for_resource(
                resource_iri=self.iri,
                lmd=self.res_dict["lastModificationDate"],
                resource_type=self.res_dict["@type"],
                context=self.res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                scope=new_scope,
                dsp_client=dsp_client,
            )
        except ApiError as err:
            self.err_msg = err.message
            logger.error(self.err_msg)


@dataclass
class ValueIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        val_oap = self._get_val_oap()
        if not val_oap:
            self.err_msg = f"Could not find value {self.iri} in resource {self.res_dict['@id']}"
            logger.error(self.err_msg)
            return
        val_oap.scope = new_scope
        try:
            update_permissions_for_value(
                resource_iri=self.iri,
                value=val_oap,
                resource_type=self.res_dict["@type"],
                context=self.res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                dsp_client=dsp_client,
            )
        except ApiError as err:
            self.err_msg = err.message
            logger.error(self.err_msg)

    def _get_val_oap(self) -> ValueOap | None:
        val_oaps = get_value_oaps(self.res_dict)
        return next((v for v in val_oaps if v.value_iri == self.iri), None)


def update_iris(
    iri_file: Path,
    new_scope: PermissionScope,
    dsp_client: DspClient,
) -> None:
    iri_updaters = _initialize_iri_updaters(iri_file, dsp_client)
    for iri in iri_updaters:
        iri.update_iri(new_scope, dsp_client)
    _tidy_up(iri_updaters, iri_file)


def _initialize_iri_updaters(iri_file: Path, dsp_client: DspClient) -> list[ResourceIRIUpdater | ValueIRIUpdater]:
    iris_raw = iri_file.read_text().splitlines()
    iri_updaters = [IRIUpdater.from_string(iri, dsp_client) for iri in iris_raw]
    res_counter = sum(isinstance(x, ResourceIRIUpdater) for x in iri_updaters)
    val_counter = sum(isinstance(x, ValueIRIUpdater) for x in iri_updaters)
    logger.info(
        f"Perform {len(iri_updaters)} updates ({res_counter} resources and {val_counter} values) "
        f"on server {dsp_client.server}..."
    )
    return iri_updaters


def _tidy_up(iri_updaters: list[ResourceIRIUpdater | ValueIRIUpdater], iri_file: Path) -> None:
    if failed_updates := [x for x in iri_updaters if x.err_msg]:
        failed_iris_file = iri_file.with_stem(f"{iri_file.stem}_failed")
        failed_iris_file.write_text("\n".join([f"{x.iri}\t\t{x.err_msg}" for x in failed_updates]))
        logger.info(f"Some updates failed. The failed IRIs and error messages have been saved to {failed_iris_file}.")
    else:
        logger.info(f"All {len(iri_updaters)} updates were successful.")
