import json
import re
import shutil
import unittest
from pathlib import Path
from typing import Iterator

import pytest

from dsp_permissions_scripts.ap.ap_model import Ap
from dsp_permissions_scripts.ap.ap_model import ApValue
from dsp_permissions_scripts.ap.ap_serialize import deserialize_aps_of_project
from dsp_permissions_scripts.ap.ap_serialize import serialize_aps_of_project
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts


class TestApSerialization(unittest.TestCase):
    shortcode = "1234"
    project_iri = "http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ"
    testdata_file = Path("testdata/APs_1234_serialized.json")
    output_dir = Path(f"project_data/{shortcode}")
    output_file = output_dir / "APs_original.json"
    ap1 = Ap(
        forGroup=group.PROJECT_ADMIN,
        forProject=project_iri,
        hasPermissions=frozenset(
            {ApValue.ProjectAdminGroupRestrictedPermission, ApValue.ProjectAdminRightsAllPermission}
        ),
        iri="http://rdfh.ch/ap-1",
    )
    ap2 = Ap(
        forGroup=group.KNOWN_USER,
        forProject=project_iri,
        hasPermissions=frozenset({ApValue.ProjectResourceCreateRestrictedPermission}),
        iri="http://rdfh.ch/ap-2",
    )

    @pytest.fixture()
    def _setup_teardown(self) -> Iterator[None]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        yield
        if self.output_dir.is_dir():
            shutil.rmtree(self.output_dir)

    @pytest.mark.usefixtures("_setup_teardown")
    def test_serialize_aps_of_project(self) -> None:
        serialize_aps_of_project(
            project_aps=[self.ap1, self.ap2],
            shortcode=self.shortcode,
            mode="original",
            host=Hosts.LOCALHOST,
        )
        with open(self.output_file, mode="r", encoding="utf-8") as f:
            aps_file = json.load(f)
        explanation_text = next(iter(aps_file.keys()))
        assert re.search(r"Project 1234 on host .+ has \d+ APs", explanation_text)
        aps_as_dicts = aps_file[explanation_text]
        assert self.ap1 == Ap.model_validate(aps_as_dicts[0])
        assert self.ap2 == Ap.model_validate(aps_as_dicts[1])

    @pytest.mark.usefixtures("_setup_teardown")
    def test_deserialize_aps_of_project(self) -> None:
        shutil.copy(src=self.testdata_file, dst=self.output_file)
        aps = deserialize_aps_of_project(
            shortcode=self.shortcode,
            mode="original",
        )
        assert self.ap1 == aps[0]
        assert self.ap2 == aps[1]


if __name__ == "__main__":
    pytest.main([__file__])
