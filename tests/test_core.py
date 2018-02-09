"""Test common skift functionalities."""

import os
import json

import pytest
from birch import Birch


ROOT = 'toasttest'
VAL_DICT = {
    'basekey': 'base_val',
    'server': {
        'hostname': 'www.test.com',
        'port': 1293,
    },
    'godeep': {
        'level2': {
            'a': 3,
            'f': 4,
        },
        'balls': 3,
    },
}


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    # Will be executed before the first test
    # - prepare cfg file
    cfg_dpath = os.path.expanduser('~/.{}'.format(ROOT))
    os.makedirs(cfg_dpath, exist_ok=True)
    fpath = os.path.join(cfg_dpath, 'cfg.json')
    with open(fpath, 'w+') as cfile:
        json.dump(VAL_DICT, cfile)
    # - prepare cfg env vars
    os.environ[ROOT.upper() + '_NEGA'] = 'Uvavo'
    os.environ[ROOT.upper() + '_MIKE'] = str(88)
    os.environ[ROOT.upper() + '_MAN_HEIGHT'] = '175'
    os.environ[ROOT.upper() + '_MAN_WEIGHT'] = '73'
    yield
    # Will be executed after the last test
    os.remove(fpath)


def test_base():
    cfg = Birch(ROOT)
    print(cfg.val_dict)
    assert cfg['basekey'] == 'base_val'
    assert cfg['BASEKEY'] == 'base_val'
    res = cfg['server']
    assert isinstance(res, dict)
    assert len(res) == 2
    assert res['PORT'] == 1293
    assert cfg['SERVER_PORT'] == 1293
    assert cfg['{}_SERVER_PORT'.format(ROOT)] == 1293
    assert cfg['nega'] == 'Uvavo'
    assert cfg['mike'] == '88'
    assert cfg['MAN']['HEIGHT'] == '175'
    assert cfg['MAN_WEIGHT'] == '73'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 10
    for name, value in cfg:
        assert isinstance(name, str)

    cfg = Birch(ROOT, supported_formats=['json'])
    print(cfg.val_dict)
    assert cfg['basekey'] == 'base_val'
    assert cfg['BASEKEY'] == 'base_val'
