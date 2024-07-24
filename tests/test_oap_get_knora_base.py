from unittest.mock import Mock

from dsp_permissions_scripts.oap.oap_get_knora_base import _get_oaps_of_one_kb_resclass
from dsp_permissions_scripts.utils.dsp_client import DspClient


def test_get_oaps_of_one_kb_resclass_0_results() -> None:
    dsp_client = Mock(spec=DspClient)
    dsp_client.get = Mock(return_value={})
    res = _get_oaps_of_one_kb_resclass(dsp_client, "proj_iri", "resclass")
    assert res == []
    assert len(dsp_client.get.call_args_list) == 1
    called_route = dsp_client.get.call_args_list[0].args[0]
    assert called_route.startswith("/v2/searchextended/")
    assert "proj_iri" in called_route
    assert "resclass" in called_route


def test_get_oaps_of_one_kb_resclass_1_result() -> None:
    pass


def test_get_oaps_of_one_kb_resclass_4_results_on_2_pages() -> None:
    pass
