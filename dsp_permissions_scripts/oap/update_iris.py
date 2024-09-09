from __future__ import annotations

import re
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from dsp_permissions_scripts.models.errors import ApiError
from dsp_permissions_scripts.models.group import KNORA_ADMIN_ONTO_NAMESPACE
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import _get_value_oaps
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_resource
from dsp_permissions_scripts.oap.oap_set import update_permissions_for_value
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


@dataclass
class IRIUpdater(metaclass=ABCMeta):
    iri: str
    success = False
    _res_dict: dict[str, Any]

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
                lmd=self._res_dict["lastModificationDate"],
                resource_type=self._res_dict["@type"],
                context=self._res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                scope=new_scope,
                dsp_client=dsp_client,
            )
            self.success = True
        except ApiError as err:
            logger.error(err)


@dataclass
class ValueIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        val_oap = self._get_val_oap()
        if not val_oap:
            logger.error(f"Could not find value {self.iri} in resource {self._res_dict['@id']}")
            return
        val_oap.scope = new_scope
        try:
            update_permissions_for_value(
                resource_iri=self.iri,
                value=val_oap,
                resource_type=self._res_dict["@type"],
                context=self._res_dict["@context"] | {"knora-admin": KNORA_ADMIN_ONTO_NAMESPACE},
                dsp_client=dsp_client,
            )
            self.success = True
        except ApiError as err:
            logger.error(err)

    def _get_val_oap(self) -> ValueOap | None:
        val_oaps = _get_value_oaps(self._res_dict)
        return next((v for v in val_oaps if v.value_iri == self.iri), None)


def update_iris(
    iri_file: Path,
    new_scope: PermissionScope,
    dsp_client: DspClient,
) -> None:
    iris_raw = iri_file.read_text().splitlines()
    iris = [IRIUpdater.from_string(iri, dsp_client) for iri in iris_raw]
    for iri in iris:
        iri.update_iri(new_scope, dsp_client)
