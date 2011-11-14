.. _module_reference:

Module reference
================

.. automodule:: pointfree


Wrapper classes
---------------

.. autoclass:: partial

.. autoclass:: pointfree


.. _helper_functions:

Composable helper functions
---------------------------

.. autofunction:: pfmap(func, iterable)

.. autofunction:: pfreduce(func, iterable[, initial=None])

.. autofunction:: pfcollect(iterable[, n=None])

.. autofunction:: pfprint(item[, end='\\n', file=sys.stdout])

.. autofunction:: pfprint_all(iterable[, end='\\n', file=sys.stdout])

.. autofunction:: pfignore_all(iterable)
