"""Test common skift functionalities."""

import os
import json
import shutil

import pytest
import yaml
from birch import Birch
from birch.exceptions import UnsupporedFormatException


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

ROOT2 = 'monkeyshoes'
VAL_DICT2 = {
    'lone': 'puf',
    'write': {
        'a': 'koko',
    }
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

    # - prepare cfg file
    cfg_dpath2 = os.path.expanduser('~/.{}'.format(ROOT2))
    os.makedirs(cfg_dpath2, exist_ok=True)
    fpath2 = os.path.join(cfg_dpath2, 'cfg.yml')
    with open(fpath2, 'w+') as cfile:
        yaml.dump(VAL_DICT2, cfile)
    # - prepare cfg env vars
    os.environ[ROOT2.upper() + '_MOLE'] = 'geers'
    os.environ[ROOT2.upper() + '_SHAKE_BAKE'] = 'bob'

    yield
    # Will be executed after the last test
    shutil.rmtree(cfg_dpath)
    shutil.rmtree(cfg_dpath2)


def test_json():
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


def test_yaml():
    cfg = Birch(ROOT2, supported_formats=['yaml'])
    print(cfg.val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['WRITE']['A'] == 'koko'
    assert cfg['WRITE_A'] == 'koko'
    assert cfg['MOLE'] == 'geers'
    assert cfg['SHAKE']['BAKE'] == 'bob'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 4
    for name, value in cfg:
        assert isinstance(name, str)


def test_unsupported_format():
    with pytest.raises(UnsupporedFormatException):
        Birch(ROOT2, supported_formats=['yaml', 'lie'])
