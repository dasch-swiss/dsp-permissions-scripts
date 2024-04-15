import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_serialize import deserialize_oaps
from dsp_permissions_scripts.oap.oap_serialize import serialize_oaps
from tests.test_scope_serialization import compare_scopes


class TestOapSerialization(unittest.TestCase):
    shortcode = "1234"

    def tearDown(self) -> None:
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)

    def test_oap_serialization(self) -> None:
        res_oap1 = ResourceOap(
            scope=PermissionScope.create(
                CR=[group.PROJECT_ADMIN],
                V=[group.PROJECT_MEMBER],
            ),
            resource_iri=f"http://rdfh.ch/{self.shortcode}/resource-1",
        )
        res_oap2 = ResourceOap(
            scope=PermissionScope.create(
                D=[group.SYSTEM_ADMIN],
                M=[group.KNOWN_USER],
            ),
            resource_iri=f"http://rdfh.ch/{self.shortcode}/resource-2",
        )
        oaps = [Oap(resource_oap=res_oap1, value_oaps=[]), Oap(resource_oap=res_oap2, value_oaps=[])]
        serialize_oaps(
            oaps=oaps,
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_oaps = deserialize_oaps(
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_oaps.sort(key=lambda oap: oap.resource_iri)
        self._compare_oaps(deserialized_oaps[0], res_oap1)
        self._compare_oaps(deserialized_oaps[1], res_oap2)

    def _compare_oaps(self, oap1: ResourceOap, oap2: ResourceOap) -> None:
        compare_scopes(oap1.scope, oap2.scope)
        self.assertEqual(oap1.resource_iri, oap2.resource_iri)


if __name__ == "__main__":
    unittest.main()
