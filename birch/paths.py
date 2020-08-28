"""Path-related functions for birch."""

import os


def _legacy_cfg_dpath(namespace):
    return os.path.join(
        os.path.expanduser('~'),
        '.{}'.format(namespace),
    )


XDG_CONFIG_HOME_VARNAME = 'XDG_CONFIG_HOME'


def _xdg_cfg_dpath(namespace):
    if XDG_CONFIG_HOME_VARNAME in os.environ:  # pragma: no cover
        return os.path.join(
            os.environ[XDG_CONFIG_HOME_VARNAME],
            namespace,
        )
    return os.path.join(  # pragma: no cover
        os.path.expanduser('~'),
        '.config',
        namespace,
    )


XDG_CACHE_HOME_VARNAME = 'XDG_CACHE_HOME'


def _xdg_cache_dpath(namespace):
    if XDG_CACHE_HOME_VARNAME in os.environ:  # pragma: no cover
        return os.path.join(
            os.environ[XDG_CACHE_HOME_VARNAME],
            namespace,
        )
    return os.path.join(  # pragma: no cover
        os.path.expanduser('~'),
        '.cache',
        namespace,
    )
