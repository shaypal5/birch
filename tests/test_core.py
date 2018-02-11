"""Test common skift functionalities."""

import os
import json
import shutil

import pytest
import yaml
from birch import Birch
from birch.exceptions import UnsupporedFormatException


NSPACE = 'toasttest'
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
    'MOCK_LVL': 'A',
    'mock_lvl2': 'B',
}

NSPACE2 = 'monkeyshoes'
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
    cfg_dpath = os.path.expanduser('~/.{}'.format(NSPACE))
    os.makedirs(cfg_dpath, exist_ok=True)
    fpath = os.path.join(cfg_dpath, 'cfg.json')
    with open(fpath, 'w+') as cfile:
        json.dump(VAL_DICT, cfile)
    # - prepare cfg env vars
    os.environ[NSPACE.upper() + '_NEGA'] = 'Uvavo'
    os.environ[NSPACE.upper() + '_MIKE'] = str(88)
    os.environ[NSPACE.upper() + '_MAN_HEIGHT'] = '175'
    os.environ[NSPACE.upper() + '_MAN_WEIGHT'] = '73'

    # - prepare cfg file
    cfg_dpath2 = os.path.expanduser('~/.{}'.format(NSPACE2))
    os.makedirs(cfg_dpath2, exist_ok=True)
    fpath2 = os.path.join(cfg_dpath2, 'cfg.yml')
    with open(fpath2, 'w+') as cfile:
        yaml.dump(VAL_DICT2, cfile)
    # - prepare cfg env vars
    os.environ[NSPACE2.upper() + '_MOLE'] = 'geers'
    os.environ[NSPACE2.upper() + '_SHAKE_BAKE'] = 'bob'

    cfg_dpath3 = os.path.expanduser('~/{}'.format(NSPACE2))
    os.makedirs(cfg_dpath3, exist_ok=True)
    fpath3 = os.path.join(cfg_dpath3, 'cfg.yml')
    with open(fpath3, 'w+') as cfile:
        yaml.dump(VAL_DICT2, cfile)

    yield
    # Will be executed after the last test
    shutil.rmtree(cfg_dpath)
    shutil.rmtree(cfg_dpath2)
    shutil.rmtree(cfg_dpath3)


def test_json():
    cfg = Birch(NSPACE)
    print(cfg.val_dict)
    assert cfg['basekey'] == 'base_val'
    assert cfg['BASEKEY'] == 'base_val'
    res = cfg['server']
    assert isinstance(res, dict)
    assert len(res) == 2
    assert res['PORT'] == 1293
    assert cfg['SERVER_PORT'] == 1293
    assert cfg['{}_SERVER_PORT'.format(NSPACE)] == 1293
    assert cfg['nega'] == 'Uvavo'
    assert cfg['mike'] == '88'
    assert cfg['MAN']['HEIGHT'] == '175'
    assert cfg['MAN_WEIGHT'] == '73'

    assert cfg['MOCK_LVL'] == 'A'
    assert cfg['MOCK_LVL2'] == 'B'

    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 12
    for name, value in cfg:
        assert isinstance(name, str)


def test_yaml():
    cfg = Birch(
        NSPACE2,
        directories=[os.path.expanduser('~/.{}'.format(NSPACE2))],
        supported_formats=['yaml'],
    )
    print(cfg.val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['WRITE']['A'] == 'koko'
    assert cfg['WRITE_A'] == 'koko'
    assert cfg['MOLE'] == 'geers'
    assert cfg['SHAKE']['BAKE'] == 'bob'
    assert cfg['SHAKE_BAKE'] == 'bob'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 4
    for name, value in cfg:
        assert isinstance(name, str)


def test_directories_str_param():
    cfg = Birch(
        NSPACE2,
        directories=os.path.expanduser('~/{}'.format(NSPACE2)),
        supported_formats='yaml',
    )
    print(cfg.val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['WRITE']['A'] == 'koko'
    assert cfg['WRITE_A'] == 'koko'
    assert cfg['MOLE'] == 'geers'
    assert cfg['SHAKE']['BAKE'] == 'bob'
    assert cfg['SHAKE_BAKE'] == 'bob'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 4
    for name, value in cfg:
        assert isinstance(name, str)


def test_unsupported_format():
    with pytest.raises(UnsupporedFormatException):
        Birch(NSPACE2, supported_formats=['yaml', 'lie'])
