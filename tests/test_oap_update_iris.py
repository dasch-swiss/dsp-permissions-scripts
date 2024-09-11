from unittest.mock import Mock

import pytest

from dsp_permissions_scripts.models.errors import InvalidIRIError
from dsp_permissions_scripts.oap.update_iris import IRIUpdater
from dsp_permissions_scripts.oap.update_iris import ResourceIRIUpdater
from dsp_permissions_scripts.oap.update_iris import ValueIRIUpdater
from dsp_permissions_scripts.utils.dsp_client import DspClient


def test_factory_with_res_iri() -> None:
    dsp_client: DspClient = Mock()
    res_iri = "http://rdfh.ch/4123/2ETqDXKeRrS5JSd6TxFO5g"
    result = IRIUpdater.from_string(res_iri, dsp_client)
    assert isinstance(result, ResourceIRIUpdater)
    assert result.iri == res_iri


def test_factory_with_value_iri() -> None:
    dsp_client: DspClient = Mock()
    val_iri = "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fkw"
    result = IRIUpdater.from_string(val_iri, dsp_client)
    assert isinstance(result, ValueIRIUpdater)
    assert result.iri == val_iri


def test_factory_with_invalid_iri() -> None:
    dsp_client: DspClient = Mock()
    invalid_iris = [
        "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fk",
        "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWx",
    ]
    for inv in invalid_iris:
        with pytest.raises(InvalidIRIError):
            IRIUpdater.from_string(inv, dsp_client)
