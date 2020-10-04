"""Testing default caster functionality for birch."""

import pytest

from birch import Birch
from birch.casters import true_false_caster

from .test_core import (
    NSPACE4,
)


def test_default_casters():
    cfg = Birch(
        namespace=NSPACE4,
        default_casters={
            'biil': true_false_caster,
            'bool': true_false_caster,
            'baal': true_false_caster,
            'shik': {
                'shuk': int,
            }
        },
    )
    val = cfg['pik']
    assert isinstance(val, str)
    val = cfg['biil']
    assert isinstance(val, bool)
    assert val is True
    val = cfg['bool']
    assert isinstance(val, bool)
    assert val is False
    with pytest.raises(ValueError):
        val = cfg['baal']
    val = cfg['shik__shuk']
    assert isinstance(val, int)
    assert val == 8
    val = cfg['shik']['shuk']
    assert isinstance(val, str)
    assert val == '8'
