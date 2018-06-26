"""Test common skift functionalities."""

import os
import json
import shutil

import pytest
import yaml
from birch import Birch
from birch.exceptions import UnsupporedFormatException
from birch.core import _xdg_cfg_dpath


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
    'MOCK__LVL': 'A',
    'mock__lvl2': 'B',
    'not_lvl2': 'C',
    # these two values should be overwritten by environment variables
    'NEGA': 'Pyong',
    'MAN': {
        'HEIGHT': '188',
    },
}

NSPACE2 = 'monkeyshoes'
VAL_DICT2 = {
    'lone': 'puf',
    'write': {
        'a': 'koko',
    }
}

NSPACE4 = 'ricketyporpoise'
VAL_DICT4 = {
    'pik': 'puk',
    'shik': {
        'shuk': '8',
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
    os.environ[NSPACE.upper() + '__NEGA'] = 'Uvavo'
    os.environ[NSPACE.upper() + '__MIKE'] = str(88)
    os.environ[NSPACE.upper() + '__MAN__HEIGHT'] = '175'
    os.environ[NSPACE.upper() + '__MAN__WEIGHT'] = '73'

    # NAMESPACE 2
    # - prepare cfg file
    cfg_dpath2 = os.path.expanduser('~/.{}'.format(NSPACE2))
    os.makedirs(cfg_dpath2, exist_ok=True)
    fpath2 = os.path.join(cfg_dpath2, 'cfg.yml')
    with open(fpath2, 'w+') as cfile:
        yaml.dump(VAL_DICT2, cfile)
    # - prepare cfg env vars
    os.environ[NSPACE2.upper() + '__MOLE'] = 'geers'
    os.environ[NSPACE2.upper() + '__SHAKE__BAKE'] = 'bob'
    os.environ[NSPACE2.upper() + '_PING_PONG'] = 'lola'

    # NAMESPACE 3
    cfg_dpath3 = os.path.expanduser('~/{}'.format(NSPACE2))
    os.makedirs(cfg_dpath3, exist_ok=True)
    fpath3 = os.path.join(cfg_dpath3, 'cfg.yml')
    with open(fpath3, 'w+') as cfile:
        yaml.dump(VAL_DICT2, cfile)

    # NAMESPACE 4
    cfg_dpath4 = _xdg_cfg_dpath(NSPACE4)
    os.makedirs(cfg_dpath4, exist_ok=True)
    fpath4 = os.path.join(cfg_dpath4, 'cfg.json')
    with open(fpath4, 'w+') as cfile:
        json.dump(VAL_DICT4, cfile)

    yield
    # Will be executed after the last test
    shutil.rmtree(cfg_dpath)
    shutil.rmtree(cfg_dpath2)
    shutil.rmtree(cfg_dpath3)
    shutil.rmtree(cfg_dpath4)


def test_json():
    cfg = Birch(NSPACE, load_all=True)
    print(cfg._val_dict)
    assert cfg['basekey'] == 'base_val'
    assert cfg['BASEKEY'] == 'base_val'
    res = cfg['server']
    assert isinstance(res, dict)
    assert len(res) == 2
    assert res['PORT'] == 1293
    assert res['port'] == 1293
    assert cfg['SERVER__PORT'] == 1293
    assert cfg['server__port'] == 1293
    assert cfg['SERVER']['PORT'] == 1293
    assert cfg['server']['PORT'] == 1293
    assert cfg['SERVER']['port'] == 1293
    assert cfg['server']['port'] == 1293
    with pytest.raises(KeyError):
        cfg['SERVER'][4]
    assert cfg['{}_SERVER__PORT'.format(NSPACE)] == 1293
    assert cfg['{}__SERVER__PORT'.format(NSPACE)] == 1293
    assert cfg['nega'] == 'Uvavo'
    assert cfg['NEGA'] == 'Uvavo'
    assert cfg['mike'] == '88'
    assert cfg['MAN']['HEIGHT'] == '175'
    assert cfg['MAN__WEIGHT'] == '73'
    with pytest.raises(ValueError):
        cfg[54]

    assert cfg['MOCK__LVL'] == 'A'
    assert cfg['mock__lvl'] == 'A'
    assert cfg['MOCK']['LVL'] == 'A'
    assert cfg['mock']['LVL'] == 'A'
    assert cfg['MOCK']['lvl'] == 'A'
    assert cfg['mock']['lvl'] == 'A'
    assert cfg['MOCK__LVL2'] == 'B'
    assert cfg['mock__lvl2'] == 'B'
    assert cfg['NOT_LVL2'] == 'C'
    assert cfg.get('NOT_LVL2') == 'C'
    assert cfg.get('NOT_LVL2', '32') == 'C'
    assert cfg.get('doesnt exists', '3321') == '3321'

    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert len(cfg) == 17
    for name, value in cfg:
        assert isinstance(name, str)


def test_yaml():
    cfg = Birch(
        NSPACE2,
        directories=[os.path.expanduser('~/.{}'.format(NSPACE2))],
        supported_formats=['yaml'],
    )
    print(cfg._val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['LONE'] == 'puf'
    assert cfg['WRITE']['A'] == 'koko'
    assert cfg['write']['A'] == 'koko'
    assert cfg['WRITE']['a'] == 'koko'
    assert cfg['write']['a'] == 'koko'
    assert cfg['WRITE__A'] == 'koko'
    assert cfg['MOLE'] == 'geers'
    assert cfg['SHAKE']['BAKE'] == 'bob'
    assert cfg['SHAKE__BAKE'] == 'bob'
    assert cfg['PING_PONG'] == 'lola'
    with pytest.raises(KeyError):
        assert cfg['PING']['PONG'] == 'lola'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    for name, value in cfg:
        assert isinstance(name, str)


def test_directories_str_param():
    cfg = Birch(
        NSPACE2,
        directories=os.path.expanduser('~/{}'.format(NSPACE2)),
        supported_formats='yaml',
    )
    print(cfg._val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['WRITE']['A'] == 'koko'
    assert cfg['WRITE__A'] == 'koko'
    assert cfg['MOLE'] == 'geers'
    assert cfg['SHAKE']['BAKE'] == 'bob'
    assert cfg['shake']['BAKE'] == 'bob'
    assert cfg['SHAKE']['bake'] == 'bob'
    assert cfg['shake']['bake'] == 'bob'
    assert cfg['SHAKE__BAKE'] == 'bob'
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    for name, value in cfg:
        assert isinstance(name, str)


def test_unsupported_format():
    with pytest.raises(UnsupporedFormatException):
        Birch(NSPACE2, supported_formats=['yaml', 'lie'])


def test_xdg_cfg_dir():
    cfg = Birch(NSPACE4)
    print(cfg._val_dict)
    assert cfg['pik'] == 'puk'
    assert cfg['shik']['shuk'] == str(8)
    assert cfg['shik__shuk'] == str(8)
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    for name, value in cfg:
        assert isinstance(name, str)


def test_xdg_cfg_dir_with_load_all():
    cfg = Birch(NSPACE4, load_all=True)
    print(cfg._val_dict)
    assert cfg['pik'] == 'puk'
    assert cfg['shik']['shuk'] == str(8)
    assert cfg['shik__shuk'] == str(8)
    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    for name, value in cfg:
        assert isinstance(name, str)
