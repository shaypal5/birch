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


class Birch(collections.abc.Mapping):
    """Defines a configuration access object.

    Parameters
    ----------
    root_name : str
        Root name to be used for configuration folder and variable names.
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

    def __init__(self, root_name, supported_formats=None):
        if supported_formats is None:
            supported_formats = ['json']
        self.root_name = root_name
        self.upper_root_name = root_name.upper()
        self.root_len = len(root_name)
        self.envar_pat = r'{}(_[A-Z0-9]+)+'.format(self.root_name.upper())
        self.formats = supported_formats
        self.no_val = Birch._NoVal()
        self.cfg_dpath = os.path.expanduser('~/.{}'.format(root_name))
        self.val_dict = self._val_dict()

    def _cfg_fpaths(self):
        paths = []
        for ext in self.formats:
            fname = Birch._CFG_FNAME_PAT.format(ext)
            fpath = os.path.join(self.cfg_dpath, fname)
            paths.append(fpath)
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
        deserial = Birch._EXT_TO_DESERIALZE_MAP[ext]
        with open(fpath, 'r') as cfile:
            val_dict = deserial(cfile)
        return Birch._upper_helper(val_dict)

    def _read_env_vars(self):
        pat = re.compile(self.envar_pat)
        val_dict = {}
        env_vars = os.environ
        for envar in env_vars:
            if re.match(pat, envar):
                key = envar[self.root_len + 1:]
                if '_' in key:
                    key_tuple = key.split('_')
                else:
                    key_tuple = [key]
                put_nested_val(val_dict, key_tuple, env_vars[envar])
        return val_dict

    def _val_dict(self):
        val_dict = {}
        for path in self._cfg_fpaths():
            val_dict.update(**self._read_cfg_file(path))
        val_dict.update(**self._read_env_vars())
        return val_dict

    # implementing a collections.abc.Mapping abstract method
    def __getitem__(self, key):
        key = key.upper()
        if self.upper_root_name in key:
            key = key[self.root_len + 1:]
        if '_' in key:
            key_tuple = key.split('_')
        else:
            key_tuple = [key]
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
