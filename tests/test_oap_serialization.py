import shutil
from pathlib import Path
from typing import Iterator

import pytest
from pytest_unordered import unordered

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap
from dsp_permissions_scripts.oap.oap_serialize import deserialize_oaps
from dsp_permissions_scripts.oap.oap_serialize import serialize_oaps


class TestOapSerialization:
    shortcode = "1234"

    @pytest.fixture(autouse=True)
    def _setup_teardown(self) -> Iterator[None]:
        yield
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)

    def test_oap_serialization(self) -> None:
        oap1 = self._get_oap_one_value_only()
        oap2 = self._get_oap_full()
        oap3 = self._get_oap_res_only()
        oaps_original = [oap1, oap2, oap3]
        serialize_oaps(oaps_original, self.shortcode, "original")
        deserialized_oaps = deserialize_oaps(self.shortcode, "original")
        assert unordered(oaps_original) == deserialized_oaps

    def _get_oap_full(self) -> Oap:
        scope = PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.PROJECT_MEMBER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-1"
        res_oap = ResourceOap(scope=scope, resource_iri=res_iri)
        val1_oap = ValueOap(
            scope=scope,
            property="foo:prop1",
            value_type="bar:val1",
            value_iri=f"{res_iri}/values/foobar1",
            resource_iri=res_iri,
        )
        val2_oap = ValueOap(
            scope=scope,
            property="foo:prop2",
            value_type="bar:val2",
            value_iri=f"{res_iri}/values/foobar2",
            resource_iri=res_iri,
        )
        oap = Oap(resource_oap=res_oap, value_oaps=[val1_oap, val2_oap])
        return oap

    def _get_oap_one_value_only(self) -> Oap:
        scope = PermissionScope.create(D=[group.SYSTEM_ADMIN], M=[group.KNOWN_USER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-2"
        val_oap = ValueOap(
            scope=scope,
            property="foo:prop3",
            value_type="bar:val3",
            value_iri=f"{res_iri}/values/foobar3",
            resource_iri=res_iri,
        )
        return Oap(resource_oap=None, value_oaps=[val_oap])

    def _get_oap_res_only(self) -> Oap:
        scope = PermissionScope.create(V=[group.KNOWN_USER], RV=[group.UNKNOWN_USER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-3"
        res_oap = ResourceOap(scope=scope, resource_iri=res_iri)
        return Oap(resource_oap=res_oap, value_oaps=[])


if __name__ == "__main__":
    pytest.main([__file__])
