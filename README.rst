birch
######
|PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

Simple hierarchical configuration for Python packages.

.. code-block:: python

  from birch import Birch

.. contents::

.. section-numbering::


Installation
============

.. code-block:: bash

  pip install birch


Features
========

* Pure python.
* Supports Python 3.4+.
* Fully tested.


Use
===

.. code-block:: python

    from birch import Birch


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


Credits
=======

Created by Shay Palachy (shay.palachy@gmail.com).


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
