"""Core capabilities for birch"""

import os
import re
import json
import collections

from strct.dicts import (
    safe_nested_val,
    put_nested_val,
    key_tuple_value_nested_generator,
)

from .exceptions import UnsupporedFormatException


class Birch(collections.abc.Mapping):
    """Defines a configuration access object.

    Parameters
    ----------
    namespace : str
        Root name to be used for configuration folder and variable names.
    directories : str or list of str, optional
        A list of directory paths in which to look for configuration files. If
        not given '~/.namespace' is the only path used.
    supported_formats : list of str, optional
        A list of configuration file formats to support; e.g. ['json', 'yml'].
        If not given, json is the only supported format.
    """

    class _NoVal(object):
        pass

    _CFG_FNAME_PAT = 'cfg.{}'
    _EXT_TO_DESERIALZE_MAP = {
        '.json': json.load,
    }
    _FMT_TO_EXT_MAP = {
        'json': ['json'],
        'yaml': ['yml', 'yaml'],
    }

    try:
        import yaml
        _EXT_TO_DESERIALZE_MAP['.yml'] = yaml.load
        _EXT_TO_DESERIALZE_MAP['.yaml'] = yaml.load
    except ImportError:  # pragma: no cover
        pass

    def __init__(self, namespace, directories=None, supported_formats=None):
        if directories is None:
            cfg_dpath = os.path.expanduser('~/.{}'.format(namespace))
            directories = [cfg_dpath]
        if isinstance(directories, str):
            directories = [directories]
        if supported_formats is None:
            supported_formats = ['json']
        if isinstance(supported_formats, str):
            supported_formats = [supported_formats]
        self.namespace = namespace
        self.upper_namespace = namespace.upper()
        self.root_len = len(namespace)
        self.envar_pat = r'{}(_[A-Z0-9]+)+'.format(self.namespace.upper())
        self.directories = directories
        self.formats = supported_formats
        self.no_val = Birch._NoVal()
        self.val_dict = self._val_dict()

    def _cfg_fpaths(self):
        paths = []
        for cfg_dpath in self.directories:
            for fmt in self.formats:
                try:
                    for ext in Birch._FMT_TO_EXT_MAP[fmt]:
                        fname = Birch._CFG_FNAME_PAT.format(ext)
                        fpath = os.path.join(cfg_dpath, fname)
                        paths.append(fpath)
                except KeyError:
                    raise UnsupporedFormatException(
                        "Unsupported format {}".format(fmt))
        return paths

    @staticmethod
    def _upper_helper(dict_obj):
        new_dict = {}
        for key, value in dict_obj.items():
            if isinstance(value, dict):
                new_dict[key.upper()] = Birch._upper_helper(value)
            else:
                new_dict[key.upper()] = value
        return new_dict

    def _read_cfg_file(self, fpath):
        _, ext = os.path.splitext(fpath)
        try:
            deserial = Birch._EXT_TO_DESERIALZE_MAP[ext]
        except KeyError:  # pragma: no cover
            return {}
        try:
            with open(fpath, 'r') as cfile:
                val_dict = deserial(cfile)
            print(fpath)
            print(val_dict)
            return Birch._upper_helper(val_dict)
        except FileNotFoundError:
            return {}

    def _read_env_vars(self):
        pat = re.compile(self.envar_pat)
        val_dict = {}
        env_vars = os.environ
        for envar in env_vars:
            if re.match(pat, envar):
                key = envar[self.root_len + 1:]
                # val_dict[key] = env_vars[envar]
                if '_' in key:
                    key_tuple = key.split('_')
                else:
                    key_tuple = [key]
                put_nested_val(val_dict, key_tuple, env_vars[envar])
        return val_dict

    def _val_dict(self):
        val_dict = {}
        for path in self._cfg_fpaths():
            print(path)
            val_dict.update(**self._read_cfg_file(path))
        val_dict.update(**self._read_env_vars())
        return val_dict

    # implementing a collections.abc.Mapping abstract method
    def __getitem__(self, key):
        key = key.upper()
        if self.upper_namespace in key:
            key = key[self.root_len + 1:]
        if '_' in key:
            key_tuple = key.split('_')
        else:
            key_tuple = [key]
        try:
            res = self.val_dict[key]
        except KeyError:
            res = safe_nested_val(key_tuple, self.val_dict, self.no_val)
        if res == self.no_val:
            raise KeyError("No configuration value for {}.".format(key))
        return res

    @staticmethod
    def _leafcounter(node):
        if isinstance(node, dict):
            return sum([Birch._leafcounter(node[n]) for n in node])
        else:
            return 1

    # implementing a collections.abc.mapping abstract method
    def __len__(self):
        return Birch._leafcounter(self.val_dict)

    # implementing a collections.abc.mapping abstract method
    def __iter__(self):
        for keytuple, value in key_tuple_value_nested_generator(self.val_dict):
            yield '_'.join(keytuple), value
