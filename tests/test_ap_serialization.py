import json
import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.ap.ap_serialize import (
    deserialize_aps_of_project,
    serialize_aps_of_project,
)
from dsp_permissions_scripts.models import builtin_groups


class TestApSerialization(unittest.TestCase):
    shortcode = "1234"
    project_iri = "http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ"
    testdata_file = Path("testdata/APs_1234_serialized.json")
    output_dir = Path(f"project_data/{shortcode}")
    output_file = output_dir / "APs_original.json"
    ap1 = Ap(
        forGroup=builtin_groups.PROJECT_ADMIN,
        forProject=project_iri,
        hasPermissions=frozenset(
            {ApValue.ProjectAdminGroupRestrictedPermission, ApValue.ProjectAdminRightsAllPermission}
        ),
        iri="http://rdfh.ch/ap-1",
    )
    ap2 = Ap(
        forGroup=builtin_groups.KNOWN_USER,
        forProject=project_iri,
        hasPermissions=frozenset({ApValue.ProjectResourceCreateRestrictedPermission}),
        iri="http://rdfh.ch/ap-2",
    )

    def setUp(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.output_dir.is_dir():
            shutil.rmtree(self.output_dir)

    def test_serialize_aps_of_project(self):
        serialize_aps_of_project(
            project_aps=[self.ap1, self.ap2],
            shortcode=self.shortcode,
            mode="original",
        )
        with open(self.output_file, mode="r", encoding="utf-8") as f:
            aps_file = json.load(f)
        self.assertTrue("Project 1234 has 2 APs" in aps_file)
        aps_as_dicts = aps_file["Project 1234 has 2 APs"]
        self.assertEqual(self.ap1, Ap.model_validate(aps_as_dicts[0]))
        self.assertEqual(self.ap2, Ap.model_validate(aps_as_dicts[1]))

    def test_deserialize_aps_of_project(self):
        shutil.copy(src=self.testdata_file, dst=self.output_file)
        aps = deserialize_aps_of_project(
            shortcode=self.shortcode,
            mode="original",
        )
        self.assertEqual(self.ap1, aps[0])
        self.assertEqual(self.ap2, aps[1])


if __name__ == "__main__":
    unittest.main()