birch ᛣ
#######

|PyPI-Status| |Downloads| |PyPI-Versions| |Build-Status| |Codecov| |Codefactor| |LICENCE|

Simple hierarchical configuration for Python packages.

.. |birch_icon| image:: https://github.com/shaypal5/birch/blob/cc5595bbb78f784a3174a07157083f755fc93172/birch.png
   :height: 87
   :width: 40 px
   :scale: 50 %
   
.. .. image:: https://github.com/shaypal5/birch/blob/b10a19a28cb1fc41d0c596df5bcd8390e7c22ee7/birch.png

.. code-block:: python

  from birch import Birch
  cfg = Birch('mypackage')
  # read using a single API both the MYPACKAGE_SERVER_HOSTNAME environment variable
  # and ~/.mypackage/cfg.json containing {'server': {'port': 55}}
  connect(cfg['SERVER__HOSTNAME'], cfg['server']['port'])

.. contents::

.. section-numbering::


Installation
============

.. code-block:: bash

  pip install birch


Features
========

* Supported formats: JSON, YAML.
* Pure python.
* Supports Python 3.6+ (3.5 up to version ``v0.0.26``).
* Supported and `fully tested on Linux, OS X and Windows <https://codecov.io/github/shaypal5/birch>`_.
* `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_ support.


Use
===

Basic use
---------

``birch`` provides an easy way to read simple hierarchical configurations for your Python package or application from both environment variables and configuration files. 

``birch`` uses namespaces to manage configuration values. The access to each namespace is done via a ``Birch`` object initialized with that namespace. Though written with a specific use case in mind, where a single package uses a single namespace to manage its configuration, any number of namespaces can be used in a single context. For example:

.. code-block:: python

  from birch import Birch
  zubat_cfg = Birch('zubat')
  golbat_cfg = Birch('golbat')


Each namespace encompasses all values set by either environment variables starting with ``<uppercase_namespace>_``, or defined within ``cfg`` files (of a supported format) located in a set of pre-configured directories; this set defaults to the ``~/.config/<namespace>`` (as par the `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_) and the ``~/.<namespace>`` directories.

For example, the ``zubat`` namespace encompasses environment variables such as ``ZUBAT_HOSTNAME`` and ``ZUBAT__PORT``, and all mappings in one of the files ``~/.config/.zubat/cfg.json`` or ``~/.zubat/cfg.json`` (if such a file exists).

Once defined in such a way, the ``Birch`` object can be used to access the values of mappings of both types (with or without the namespace suffix; casing is also ignored). For example:

.. code-block:: python

  >>> import os
  >>> os.environ['ZUBAT_SERVER_HOST'] = 'www.zubat.com'
  >>> os.environ['ZUBAT_SERVER_PORT'] = '87'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg['ZUBAT_SERVER_HOST']
  'www.zubat.com'
  >>> zubat_cfg['SERVER_PORT']
  '87'
  >>> zubat_cfg['server_port']
  '87'


The get and mget methods
------------------------

Birch objects expose two methods that allow more nuanced retreival of configuration items:

The ``mget`` method allows the caller to supply a ``caster`` callable, through-which any found return value will be passed:

.. code-block:: python

  >>> os.environ['ZUBAT__PORT'] = '555'
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg.mget('port', int)
  555


The ``get`` method additionally allows you to supply a default value, which is returned if no matching configuration entry is found:

.. code-block:: python

  >>> import os; os.environ['ZUBAT__PORT'] = '555'
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg.get('port', default=8888, caster=int)
  555
  >>> zubat_cfg.get('host', default='defhost')  # Default value is returned
  'defhost'
  >>> zubat_cfg.get('host')  # No error is thrown, None is returned


If no default value is provided, ``None`` is returned. To still have a ``KeyError`` raised in this case use ``throw=True`` in the function call:

.. code-block:: python

  >>> import os; os.environ['ZUBAT__PORT'] = '555'
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg.get('host', throw=True)  # An error is thrown
  Traceback (most recent call last):
    ...
  KeyError: 'zubat: No configuration value for HOST.'

To have a warning raised (and the code continue to run) in this case, use ``warn=True`` instead:

.. code-block:: python

  >> import os; os.environ['ZUBAT__PORT'] = '555'
  >> zubat_cfg = Birch('zubat')
  >> zubat_cfg.get('host', warn=True)  # A warning is raised
  None or no value was provided to configuration value host for zubat!


Hierarchical configuration
--------------------------

``birch`` supports a simple hierarchy between configuration mappings. Hierarchy is either expressed explicitly in configuration files as nested object/entries (in the case of ``json`` and ``YAML`` files), or using ``__`` (two underscore characters) in the configuration key - both in configuration files and environment variables. Thus, the ``ZUBAT__SERVER__PORT`` environment variable is equivalent to both ``{'server': {'port': 55}}`` and ``{'server__PORT': 55}`` mappings given in a ``~/.zubat/cfg.json`` file, for example. Casing is ignored on all levels.

As such, hierarchical mappings can be accessed either using ``__`` to indicate a hierarchical path, or using dict-like item access:

.. code-block:: python

  >>> os.environ['ZUBAT__SERVER__HOST'] = 'www.zubat.com'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg['SERVER__HOST']
  'www.zubat.com'
  >>> zubat_cfg['server']['HOST']
  'www.zubat.com'
  >>> zubat_cfg['SERVER']['host']
  'www.zubat.com'


**Note that this is also true for non-hierarchical configuration file mappings**, so ``{'server__port': 55}``, even when given in this form in a configuration file, can be accessed using both ``zubat_cfg['SERVER__PORT']`` and ``zubat_cfg['SERVER']['PORT']`` (casing is still ignored on all levels).


Default values
--------------

You can easily assign default values to any number of keys or nested keys by providing the ``defaults`` constructor keyword argument with a ``dict`` containing such mappings:

.. code-block:: python

  >>> from birch import Birch
  >>> defaults = {
  ...     'server': {'host': 'www.boogle.com'},
  ...     'server__port': 8888,
  ...      'GOLBAT__SERVER__PROTOCOL': 'http',
  ... }
  >>> golbat_cfg = Birch('golbat', defaults=defaults)
  >>> golbat_cfg['SERVER__HOST']
  'www.boogle.com'
  >>> golbat_cfg['SERVER']['PORT']
  8888
  >>> golbat_cfg['SERVER']['protocol']
  'http'

These values will be overwritten by configuration values loaded from both files and environment variables:

.. code-block:: python
  
  >>> os.environ['GOLBAT__SERVER__HOST'] = 'www.zubat.com'
  >>> golbat_cfg = Birch('golbat', defaults=defaults)
  >>> golbat_cfg['SERVER__HOST']
  'www.zubat.com'
  >>> golbat_cfg['SERVER']['PORT']
  8888


Resolution order
----------------

A namespace is always loaded with matching environment variables **after** the configuration file has been loaded, and corresponding mappings will thus override their file-originating counterparts; e.g. the ``ZUBAT__SERVER__PORT`` environment variable will overwrite the value of the mapping ``{'server': {'port': 55}}`` given in a ``~/.zubat/cfg.json`` file. 

The lookup order of different files, while deterministic, is undefined and not part of the API. Thus, even with the ``load_all`` option set (see the `Configuring birch`_ section), ``cfg`` files with different file extensions can not be relied upon to provide private-vs-shared configuration functionality, or other such configuration modes.

Finally, loading of configuration values from both files and environment variables is done **after** the default values provided in the ``defaults`` constructor argument are loaded, so they both override default values.


Reloading configuration
-----------------------

Configuration values can be reloaded from all sources - both configuration files and environment variables - by calling the ``reload`` method:

.. code-block:: python

  >>> os.environ['ZUBAT__SERVER__HOST'] = 'www.zubat.com'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat')
  >>> zubat_cfg['SERVER__HOST']
  'www.zubat.com'
  >>> os.environ['ZUBAT__SERVER__HOST'] = 'New.value!'
  >>> zubat_cfg.reload()
  >>> zubat_cfg['server']['HOST']
  'New.value!'

You can set automatic configuration reload on every value inspection by setting ``auto_reload=True`` when initializing the ``Birch`` object:

.. code-block:: python

  >>> os.environ['ZUBAT__SERVER__HOST'] = 'www.zubat.com'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat', auto_reload=True)
  >>> zubat_cfg['SERVER__HOST']
  'www.zubat.com'
  >>> os.environ['ZUBAT__SERVER__HOST'] = 'New.value!'
  >>> zubat_cfg['server']['HOST']
  'New.value!'


Convenience methods
-------------------

The ``xdg_config_dpath()`` and ``xdg_cache_dpath()`` methods are provided to enable easy access to where the XDG-compliant configuration and cache directories for this namespace should reside.

For example, if the ``XDG_CONFIG_HOME`` variable is set to ``/Users/daria/myconfig/`` then ``zubat_cfg.xdg_cfg_dpath()`` will return ``/Users/daria/myconfig/zubat/``, while if it is not set, the same method will return ``/Users/daria/.config/zubat/``.


Configuring birch
=================

Configuration directories
-------------------------

By default ``birch`` looks for files only in the ``~/.config/<namespace>`` and ``~/.<namespace>`` directories. You can set a different set of directories to read by populating the ``directories`` constructor parameter with a different directory path, or a list of paths.

Similarly, be default ``birch`` reads into the configuration tree only the first compliant file encountered during a lookup in all pre-configured directories; to instead load hierarchical configurations from all such files instead, the ``load_all`` constructor parameter can be set to ``True``. Again, load order is undefined, and thus so is the resulting hierarchical configuration.


File formats
------------

By default, ``birch`` will only try to read ``cfg.json`` files. To dictate a different set of supported formats, populate the ``supported_formats`` constructor parameter with the desired formats. 

For example, ``Birch('zubat', supported_formats=['json', 'yaml'])`` will read both ``cfg.json`` and ``cfg.yaml`` files, while ``Birch('golbat', supported_formats='yaml')`` will ony read ``cfg.yaml`` (and ``cfg.yml``) files.

Currently supported formats are:

* ``JSON`` - Looks for ``cfg.json`` files.
* ``YAML`` - Looks for ``cfg.yaml`` and ``cfg.yml`` files.


Contributing
============

Package author and current maintainer is Shay Palachy (shay.palachy@gmail.com); You are more than welcome to approach him for help. Contributions are very welcomed.

Installing for development
----------------------------

Clone:

.. code-block:: bash

  git clone git@github.com:shaypal5/birch.git


Install in development mode, including test dependencies:

.. code-block:: bash

  cd birch
  pip install -e '.[test]'


Running the tests
-----------------

To run the tests use:

.. code-block:: bash

  cd birch
  pytest


Adding documentation
--------------------

The project is documented using the `numpy docstring conventions`_, which were chosen as they are perhaps the most widely-spread conventions that are both supported by common tools such as Sphinx and result in human-readable docstrings. When documenting code you add to this project, follow `these conventions`_.

.. _`numpy docstring conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
.. _`these conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Additionally, if you update this ``README.rst`` file,  use ``python setup.py checkdocs`` to validate it compiles.


Credits
=======

Created by `Shay Palachy <http://www.shaypalachy.com/>`_ (shay.palachy@gmail.com).


.. |PyPI-Status| image:: https://img.shields.io/pypi/v/birch.svg
  :target: https://pypi.python.org/pypi/birch

.. |PyPI-Versions| image:: https://img.shields.io/pypi/pyversions/birch.svg
   :target: https://pypi.python.org/pypi/birch

.. |Build-Status| image:: https://travis-ci.org/shaypal5/birch.svg?branch=master
   :target: https://travis-ci.org/shaypal5/birch

.. |LICENCE| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/shaypal5/birch/blob/master/LICENSE

.. |Codecov| image:: https://codecov.io/github/shaypal5/birch/coverage.svg?branch=master
   :target: https://codecov.io/github/shaypal5/birch?branch=master

.. |Codacy| image:: https://api.codacy.com/project/badge/Grade/99e79faee7454a13a0e60219c32015ae
   :alt: Codacy Badge
   :target: https://app.codacy.com/app/shaypal5/birch?utm_source=github.com&utm_medium=referral&utm_content=shaypal5/birch&utm_campaign=Badge_Grade_Dashboard

.. |Requirements| image:: https://requires.io/github/shaypal5/birch/requirements.svg?branch=master
   :target: https://requires.io/github/shaypal5/birch/requirements/?branch=master
   :alt: Requirements Status
     
.. |Codefactor| image:: https://www.codefactor.io/repository/github/shaypal5/birch/badge?style=plastic
   :target: https://www.codefactor.io/repository/github/shaypal5/birch
   :alt: Codefactor code quality

.. |Downloads| image:: https://pepy.tech/badge/birch
   :target: https://pepy.tech/project/birch
   :alt: PePy stats

.. .. test pypi
