"""Core capabilities for birch"""

import os
import re
import json
import collections

from strct.dicts import (
    safe_nested_val,
    put_nested_val,
    key_tuple_value_nested_generator,
    CaseInsensitiveDict,
)

from .exceptions import UnsupporedFormatException

SEP = '__'


def _legacy_cfg_dpath(namespace):
    return os.path.expanduser('~/.{}'.format(namespace))


XDG_CONFIG_HOME_VARNAME = 'XDG_CONFIG_HOME'


def _xdg_cfg_dpath(namespace):
    if XDG_CONFIG_HOME_VARNAME in os.environ:  # pragma: no cover
        return '{}/{}'.format(os.environ[XDG_CONFIG_HOME_VARNAME], namespace)
    return os.path.expanduser('~/.config/{}'.format(namespace))


class Birch(collections.abc.Mapping):
    """Defines a configuration access object.

    Parameters
    ----------
    namespace : str
        Root name to be used for configuration folder and variable names.
    directories : str or list of str, optional
        A list of directory paths in which to look for configuration files. If
        not given, defaults to a list containing '$XDG_CONFIG_HOME/namespace`
        and '~/.namespace'.
    supported_formats : list of str, optional
        A list of configuration file formats to support; e.g. ['json', 'yml'].
        If not given, json is the only supported format.
    load_all : bool, default False
        If set to true, all compliant configuration files found in any of the
        allowed directories are used to consturct the configuration tree, in
        an undefined order. By default, the first such file encountered is
        read.
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

    def __init__(self, namespace, directories=None, supported_formats=None,
                 load_all=False):
        if directories is None:
            directories = [
                _xdg_cfg_dpath(namespace=namespace),
                _legacy_cfg_dpath(namespace=namespace),
            ]
        if isinstance(directories, str):
            directories = [directories]
        if supported_formats is None:
            supported_formats = ['json']
        if isinstance(supported_formats, str):
            supported_formats = [supported_formats]
        supported_formats = [fmt.lower() for fmt in supported_formats]
        self.namespace = namespace
        self._upper_namespace = namespace.upper()
        self._root1 = self._upper_namespace + '_'
        self._root2 = self._upper_namespace + '__'
        self._root_len1 = len(namespace) + 1
        self._root_len2 = len(namespace) + 2
        self._envar_pat = r'{}((_|__)[A-Z0-9]+)+'.format(self._upper_namespace)
        self.directories = directories
        self.formats = supported_formats
        self.load_all = load_all
        self._no_val = Birch._NoVal()
        self._val_dict = self._build_val_dict()

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
    def _hierarchical_dict_from_dict(dict_obj):
        val_dict = {}
        for key, value in dict_obj.items():
            key = key.lower()
            if SEP in key:
                key_tuple = key.split(SEP)
            else:
                key_tuple = [key]
            val_dict[key] = value
            put_nested_val(val_dict, key_tuple, value)
        return CaseInsensitiveDict.from_dict(val_dict)

    def _read_cfg_file(self, fpath):
        _, ext = os.path.splitext(fpath)
        try:
            deserial = Birch._EXT_TO_DESERIALZE_MAP[ext]
        except KeyError:  # pragma: no cover
            return {}
        try:
            with open(fpath, 'r') as cfile:
                val_dict = deserial(cfile)
            val_dict = Birch._hierarchical_dict_from_dict(val_dict)
            return val_dict
        except FileNotFoundError:  # pragma: no cover
            return {}

    def _read_env_vars(self):
        pat = re.compile(self._envar_pat)
        val_dict = {}
        env_vars = os.environ
        for envar in env_vars:
            if re.match(pat, envar):
                if self._root2 in envar:
                    key = envar[self._root_len2:]
                # elif self._root1 in envar:
                else:
                    key = envar[self._root_len1:]
                val_dict[key] = env_vars[envar]
        val_dict = Birch._hierarchical_dict_from_dict(val_dict)
        return val_dict

    def _build_val_dict(self):
        val_dict = CaseInsensitiveDict()
        for path in self._cfg_fpaths():
            if os.path.isfile(path):
                val_dict.update(**self._read_cfg_file(path))
                if not self.load_all:
                    break
        val_dict.update(**self._read_env_vars())
        val_dict = Birch._hierarchical_dict_from_dict(val_dict)
        return val_dict

    # implementing a collections.abc.Mapping abstract method
    def __getitem__(self, key):
        try:
            key = key.upper()
        except AttributeError:
            raise ValueError("Birch does not support non-string keys!")
        if self._root2 in key:
            key = key[self._root_len2:]
        elif self._root1 in key:
            key = key[self._root_len1:]
        if SEP in key:
            key_tuple = key.split(SEP)
        else:
            key_tuple = [key]
        try:
            res = self._val_dict[key]
        except KeyError:
            res = safe_nested_val(key_tuple, self._val_dict, self._no_val)
        if res == self._no_val:
            raise KeyError("No configuration value for {}.".format(key))
        return res

    def get(self, key, default=None):
        """Return the value for key if it's in the configuration, else default.

        If default is not given, it defaults to None, so that this method never
        raises a KeyError.

        Parameters
        ----------
        key : object
            The key of the value to get.
        default : object, optional
            If the key is not found, this value is returned. If note given, it
            defaults to None, so that this method never raised a KeyError.

        Returns
        -------
        object
            The value the given key maps to, if it is in the configuration.
            Else, the default value is returned.
        """
        try:
            return self[key]
        except KeyError:
            return default

    @staticmethod
    def _leafcounter(node):
        if isinstance(node, dict):
            return sum([Birch._leafcounter(node[n]) for n in node])
        else:
            return 1

    # implementing a collections.abc.mapping abstract method
    def __len__(self):
        return Birch._leafcounter(self._val_dict)

    # implementing a collections.abc.mapping abstract method
    def __iter__(self):
        for keytupl, value in key_tuple_value_nested_generator(self._val_dict):
            yield SEP.join(keytupl), value
