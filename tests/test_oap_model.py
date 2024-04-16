import pytest

from dsp_permissions_scripts.oap.oap_model import Oap


class TestOap:
    def test_oap_no_res_no_vals(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011 (exception too broad)
            Oap(resource_oap=None, value_oaps=[])
