from __future__ import annotations

import re
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path

from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.dsp_client import DspClient


@dataclass
class IRIUpdater(metaclass=ABCMeta):
    iri: str

    @abstractmethod
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        pass

    @staticmethod
    def from_string(string: str) -> ResourceIRIUpdater | ValueIRIUpdater:
        if re.search(r"http://rdfh\.ch/[^/]{4}/[^/]+/values/[^/]+", string):
            return ValueIRIUpdater(string)
        return ResourceIRIUpdater(string)


@dataclass
class ResourceIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        pass


@dataclass
class ValueIRIUpdater(IRIUpdater):
    def update_iri(self, new_scope: PermissionScope, dsp_client: DspClient) -> None:
        pass


def update_iris(
    iri_file: Path,
    new_scope: PermissionScope,
    dsp_client: DspClient,
) -> None:
    iris_raw = iri_file.read_text().splitlines()
    iris = [IRIUpdater.from_string(iri) for iri in iris_raw]
    for iri in iris:
        iri.update_iri(new_scope, dsp_client)
