"""Test common skift functionalities."""

import os
import json
import copy
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
    'biil': 'True',
    'bool': 'False',
    'boolan': True,
    'baal': 500,
    'shik': {
        'shuk': '8',
    }
}


def setup_cfg_file(namespace, val_dict, ext):
    cfg_dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(namespace),
    )
    os.makedirs(cfg_dpath, exist_ok=True)
    fpath = os.path.join(cfg_dpath, 'cfg.{}'.format(ext))
    with open(fpath, 'w+') as cfile:
        if (ext == 'yaml') or (ext == 'yml'):
            yaml.dump(val_dict, cfile)
        elif ext == 'json':
            json.dump(val_dict, cfile)
        else:
            raise ValueError("Unknown file extension for birch test cfg file!")
    return cfg_dpath


def prepare_namespace_2():
    # NAMESPACE 2
    # - prepare cfg file
    cfg_dpath2 = setup_cfg_file(
        namespace=NSPACE2, val_dict=VAL_DICT2, ext='yml')
    # - prepare cfg env vars
    os.environ[NSPACE2.upper() + '__MOLE'] = 'geers'
    os.environ[NSPACE2.upper() + '__SHAKE__BAKE'] = 'bob'
    os.environ[NSPACE2.upper() + '_PING_PONG'] = 'lola'
    return cfg_dpath2


@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():
    # Will be executed before the first test
    # - prepare cfg file
    cfg_dpath = setup_cfg_file(
        namespace=NSPACE, val_dict=VAL_DICT, ext='json')
    # - prepare cfg env vars
    os.environ[NSPACE.upper() + '__NEGA'] = 'Uvavo'
    os.environ[NSPACE.upper() + '__MIKE'] = str(88)
    os.environ[NSPACE.upper() + '__MAN__HEIGHT'] = '175'
    os.environ[NSPACE.upper() + '__MAN__WEIGHT'] = '73'

    # NAMESPACE 2
    cfg_dpath2 = prepare_namespace_2()

    # NAMESPACE 3
    cfg_dpath3 = os.path.join(
        os.path.expanduser('~'),
        '{}'.format(NSPACE2),
    )
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
        res = cfg['SERVER'][4]
    assert cfg['{}_SERVER__PORT'.format(NSPACE)] == 1293
    assert cfg['{}__SERVER__PORT'.format(NSPACE)] == 1293
    assert cfg['nega'] == 'Uvavo'
    assert cfg['NEGA'] == 'Uvavo'
    assert cfg['mike'] == '88'
    assert cfg['MAN']['HEIGHT'] == '175'
    assert cfg['MAN__WEIGHT'] == '73'
    with pytest.raises(ValueError):
        res = cfg[54]

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
    assert cfg.get('doesnt exists', None) is None
    with pytest.warns(UserWarning):
        assert cfg.get('doesnt exists', None, warn=True) is None

    with pytest.raises(KeyError):
        assert cfg['JON'] == 'Hello'
    assert cfg.get('JON') is None
    assert cfg.get('JON', default='Hello') == 'Hello'
    with pytest.raises(KeyError):
        assert cfg.get('JON', throw=True) is None
    assert len(cfg) == 17
    for name, value in cfg:
        assert isinstance(name, str)
    assert isinstance(cfg.as_str(), str)


def test_yaml():
    dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=[dpath],
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
    dpath = os.path.join(
        os.path.expanduser('~'),
        '{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=dpath,
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


def test_envvar_with_reload():
    dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=[dpath],
        supported_formats=['yaml'],
    )
    print(cfg._val_dict)
    assert cfg['mole'] == 'geers'
    assert cfg['MOLE'] == 'geers'
    mole_envar = '{}__MOLE'.format(NSPACE2.upper())
    mole_val = 'kirgizi'
    os.environ[mole_envar] = mole_val
    cfg.reload()
    print(cfg._val_dict)
    assert cfg[mole_envar] == mole_val
    assert cfg['mole'] == mole_val
    assert cfg['MOLE'] == mole_val


def test_yaml_with_reload():
    dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=[dpath],
        supported_formats=['yaml'],
    )
    print(cfg._val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['LONE'] == 'puf'
    lone_val = 'kakara'
    updated_valdict = copy.deepcopy(VAL_DICT2)
    updated_valdict['lone'] = lone_val
    setup_cfg_file(namespace=NSPACE2, val_dict=updated_valdict, ext='yml')
    cfg.reload()
    print(cfg._val_dict)
    assert cfg['lone'] == lone_val
    assert cfg['LONE'] == lone_val


def test_envvar_with_auto_reload():
    prepare_namespace_2()
    dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=[dpath],
        supported_formats=['yaml'],
        auto_reload=True,
    )
    print(cfg._val_dict)
    assert cfg['mole'] == 'geers'
    assert cfg['MOLE'] == 'geers'
    mole_envar = '{}__MOLE'.format(NSPACE2.upper())
    mole_val = 'kirgizi'
    os.environ[mole_envar] = mole_val
    print(cfg._val_dict)
    assert cfg[mole_envar] == mole_val
    assert cfg['mole'] == mole_val
    assert cfg['MOLE'] == mole_val


def test_yaml_with_auto_reload():
    prepare_namespace_2()
    dpath = os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(NSPACE2),
    )
    cfg = Birch(
        NSPACE2,
        directories=[dpath],
        supported_formats=['yaml'],
        auto_reload=True,
    )
    print(cfg._val_dict)
    assert cfg['lone'] == 'puf'
    assert cfg['LONE'] == 'puf'
    lone_val = 'kakara'
    updated_valdict = copy.deepcopy(VAL_DICT2)
    updated_valdict['lone'] = lone_val
    setup_cfg_file(namespace=NSPACE2, val_dict=updated_valdict, ext='yml')
    print(cfg._val_dict)
    assert cfg['lone'] == lone_val
    assert cfg['LONE'] == lone_val


def test_envvars_with_defaults():
    prepare_namespace_2()
    k1 = 'NAKOKO'
    full_k1 = '{}_{}'.format(NSPACE2, k1)
    v1 = 45
    k2_1 = 'NANA'
    k2_2 = 'BOKO'
    full_k2 = '{}__{}__{}'.format(NSPACE2, k2_1, k2_2)
    v2 = 'rar'
    k3 = 'lemer'
    v3 = 'yever'
    full_k4 = '{}_magi'.format(NSPACE2)
    v4 = 39
    k5_1 = 'anil'
    k5_2 = 'shanil'
    v5 = 'baril'
    defaults = {
        k1: v1,
        full_k2: v2,
        k3: v3,
        full_k4: v4,
        k5_1: {k5_2: v5},
    }
    cfg = Birch(
        NSPACE2,
        defaults=defaults,
    )
    assert cfg[k1] == v1
    assert cfg[full_k1] == v1
    assert cfg.mget(full_k1) == v1
    assert cfg.get(k1) == v1
    assert cfg[k2_1][k2_2] == v2
    assert cfg[full_k2] == v2
    assert cfg[k3] == v3
    assert cfg[full_k4] == v4
    assert cfg[k5_1][k5_2] == v5

    with pytest.raises(ValueError):
        cfg = Birch(
            NSPACE2,
            defaults={2: 'kpkp'},
        )


def test_xdg_cfg_dpath():
    cfg = Birch(NSPACE4)
    returned_dpath = cfg.xdg_cfg_dpath()
    try:
        xdg_cfg_home = os.environ['XDG_CONFIG_HOME']
        expected_path = os.path.join(xdg_cfg_home, NSPACE4)
    except KeyError:
        homedir = os.path.expanduser('~')
        expected_path = os.path.join(homedir, '.config', NSPACE4)
    assert expected_path in returned_dpath
    assert expected_path in Birch.xdg_cfg_dpath_by_namespace(NSPACE4)


def test_xdg_cache_dpath():
    cfg = Birch(NSPACE4)
    returned_dpath = cfg.xdg_cache_dpath()
    try:
        xdg_cache_home = os.environ['XDG_CACHE_HOME']
        expected_path = os.path.join(xdg_cache_home, NSPACE4)
    except KeyError:
        homedir = os.path.expanduser('~')
        expected_path = os.path.join(homedir, '.cache', NSPACE4)
    assert expected_path in returned_dpath
    assert expected_path in Birch.xdg_cache_dpath_by_namespace(NSPACE4)
