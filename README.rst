birch |birch_icon|
##################
|PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

Simple hierarchical configuration for Python packages.

.. |birch_icon| image:: https://github.com/shaypal5/birch/blob/cc5595bbb78f784a3174a07157083f755fc93172/birch.png
   :height: 87
   :width: 40 px
   :scale: 50 %
   
.. .. image:: https://github.com/shaypal5/birch/blob/b10a19a28cb1fc41d0c596df5bcd8390e7c22ee7/birch.png

.. code-block:: python

  from birch import Birch
  cfg = Birch('mypackage')
  # read both the MYPACKAGE_SERVER_HOSTNAME environment variable
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
* Supports Python 3.4+.
* Fully tested.


Use
===

Basic use
---------

``birch`` provides a simple way to read simple hierarchical configuration for your Python package or application from both environment variables and configuration files. 

``birch`` uses namespaces to manage configuration values. The access to each namespace is done via a ``Birch`` object initialized with that namespace. Though written with a specific use case in mind, where a single package uses a single namespace to manage its configuration, any number of namespaces can be used. For example:

.. code-block:: python

  from birch import Birch
  zubat_cfg = Birch('zubat')
  golbat_cfg = Birch('golbat')


Each namespace encompasses all values set by either environment variables starting with ``<uppercase_namespace>_`` or ``<uppercase_namespace>__``, or defined within ``cfg`` files (of a supported format) located in the ``~/.<namespace>`` directory.

For example, the ``zubat`` namespace encompasses environment variables such as ``ZUBAT_HOSTNAME`` and ``ZUBAT__PORT``, and all mappings in the ``~/.zubat/cfg.json`` file (if it exists).

Once defined in such a way, the ``Birch`` object can be used to access the values of mappings of both types (with or without the namespace suffix; casing is also ignored). For example:

.. code-block:: python

  >>> os.environ['ZUBAT_SERVER_HOST'] = 'www.zubat.com'
  >>> os.environ['ZUBAT_SERVER_PORT'] = '87'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat')
  >>>> zubat_cfg['ZUBAT_SERVER_HOST']
  'www.zubat.com'
  >>> zubat_cfg['SERVER_PORT']
  '87'
  >>> zubat_cfg['server_port']
  '87'


Hierarchical configuration
--------------------------

``birch`` supports a simple hierarchy between configuration mappings. ``__`` (two underscore characters) is used to signal a hierarchical mapping, so the ``ZUBAT__SERVER__PORT`` environment variable is equivalent to ``{'server': {'port': 55}}`` mapping given in a ``~/.zubat/cfg.json`` file, for example.

As such, hierarchical mapping can be accessed either using ``__`` to indicate a hierarchical path, or using dict-like item access:

.. code-block:: python

  >>> os.environ['ZUBAT__SERVER__HOST'] = 'www.zubat.com'
  >>> from birch import Birch
  >>> zubat_cfg = Birch('zubat')
  >>>> zubat_cfg['SERVER__HOST']
  'www.zubat.com'
  >>>> zubat_cfg['SERVER']['HOST']
  'www.zubat.com'


**This is not true for non-hierarchical mappings**; so, ``{'server__port': 55}`` can only be accessed with ``zubat_cfg['SERVER__PORT']``, and not using ``zubat_cfg['SERVER']['PORT']``.


Resolution order
----------------

A namespace is always loaded with matching environment variables **after** all configuration files has been loaded, and corresponding mappings will thus override their file-originating counterparts; e.g. the ``ZUBAT__SERVER__PORT`` environment variable will overwrite the value of the mapping ``{'server': {'port': 55}}`` given in a ``~/.zubat/cfg.json`` file. 

The loading order of different files, while deterministic, is undefined and not part of the API. Thus, ``cfg`` files with different file extensions can not be relied upon to provide private-vs-shared configuration functionality.


Configuring birch
-----------------

Configuration directories
~~~~~~~~~~~~~~~~~~~~~~~~~

By default ``birch`` looks for files only in the ``~/.<namespace>`` directory. You can set a different set of directories to read by populating the ``directories`` constructor parameter with a different directory path, or a list of paths.


File formats
~~~~~~~~~~~~

By default, ``birch`` will only try to read ``cfg.json`` files. To dictate a different set of supported format, populate the ``supported_formats`` constructor parameter with the desired formats. 

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

.. |LICENCE| image:: https://img.shields.io/github/license/shaypal5/birch.svg
  :target: https://github.com/shaypal5/birch/blob/master/LICENSE

.. |Codecov| image:: https://codecov.io/github/shaypal5/birch/coverage.svg?branch=master
   :target: https://codecov.io/github/shaypal5/birch?branch=master
