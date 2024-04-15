import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_serialize import deserialize_resource_oaps
from dsp_permissions_scripts.oap.oap_serialize import serialize_resource_oaps
from tests.test_scope_serialization import compare_scopes

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)

class TestOapSerialization(unittest.TestCase):
    shortcode = "1234"

    def tearDown(self) -> None:
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)

    def test_oap_serialization(self) -> None:
        oap1 = Oap(
            scope=PermissionScope.create(
                CR=[group.PROJECT_ADMIN],
                V=[group.PROJECT_MEMBER],
            ),
            object_iri=f"http://rdfh.ch/{self.shortcode}/resource-1",
        )
        oap2 = Oap(
            scope=PermissionScope.create(
                D=[group.SYSTEM_ADMIN],
                M=[group.KNOWN_USER],
            ),
            object_iri=f"http://rdfh.ch/{self.shortcode}/resource-2",
        )
        serialize_resource_oaps(
            resource_oaps=[oap1, oap2],
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_oaps = deserialize_resource_oaps(
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_oaps.sort(key=lambda oap: oap.object_iri)
        self._compare_oaps(deserialized_oaps[0], oap1)
        self._compare_oaps(deserialized_oaps[1], oap2)

    def _compare_oaps(self, oap1: Oap, oap2: Oap) -> None:
        compare_scopes(oap1.scope, oap2.scope)
        self.assertEqual(oap1.object_iri, oap2.object_iri)


if __name__ == "__main__":
    unittest.main()
