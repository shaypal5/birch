"""Core capabilities for birch"""

import os
import json
import collections

from strct.dicts import safe_nested_val


class Birch(collections.abc.Mapping):
    """Defines a configuration access object.

    Parameters
    ----------
    root_name : str
        Root name to be used for configuration folder and variable names.
    conf_dict : dict
        A dict defining the hierarchy of configuration values to support.
    supported_formats : list of str, optional
        A list of configuration file formats to support; e.g. ['json', 'yml'].
        If not given, json is the only supported format.
    """

    class _NoVal(object):
        pass

    _CFG_FNAME_PAT = 'cfg.{}'
    _EXT_TO_DESERIALZE_MAP = {
        'json': json.load,
    }

    def __init__(self, root_name, conf_dict, supported_formats=None):
        if supported_formats is None:
            supported_formats = ['json']
        self.root_name = root_name
        self.conf_dict = conf_dict
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

    def _read_cfg_file(self, fpath):
        _, ext = os.path.splitext(fpath)
        deserial = Birch._EXT_TO_DESERIALZE_MAP[ext]
        return deserial(fpath)

    def _val_dict(self):
        val_dict = {}
        for path in self._cfg_fpaths():
            val_dict.update(**self._read_cfg_file(path))
        return val_dict

    # implementing a collections.abc.Mapping abstract method
    def __getitem__(self, key):
        if '.' in key:
            key_tuple = key.split('.')
        else:
            key_tuple = [key]
        if key_tuple[0] == self.root_name:
            key_tuple = key_tuple[1:]
        res = safe_nested_val(key_tuple, self.val_dict, self.no_val)
        if res == self.no_val:
            raise KeyError("No configuration value for {}.".format(key))
        return res

    @staticmethod
    def _leafcounter(node):
        if isinstance(node, dict):
            return sum([Birch.leafcounter(node[n]) for n in node])
        else:
            return 1

    # implementing a collections.abc.mapping abstract method
    def __len__(self):
        return Birch._leafcounter(self.conf_dict)
