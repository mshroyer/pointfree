.. _overview:

Overview
========


Introduction
------------

:py:mod:`pointfree` is a small module that makes certain functional
programming constructs more convenient to use in Python.

Specifically, it provides:

* A decorator to enable *automatic* partial application of functions and
  methods.
* Notations for function composition through operator overloading.
* Helper functions to make composing generators more elegant.

The objective is to support the `pointfree programming style`_ in a
lightweight and easy to use manner -- and in particular, to serve as a nice
syntax for the kind of generator pipelines described in David Beazley's
PyCon 2008 presentation, `"Generator Tricks for Systems Programmers"`_.

.. _`pointfree programming style`: http://www.haskell.org/haskellwiki/Pointfree

.. _`"Generator Tricks for Systems Programmers"`: http://www.dabeaz.com/generators/Generators.pdf


Examples
--------

The :py:mod:`pointfree` module is about using function composition notation
in conjunction with automatic partial application.  Both of these features
are achieved by wrapping functions in the :py:class:`~pointfree.pointfree`
class (which can also be applied as a decorator).

Several "pre-wrapped" helper functions are provided by the module.  For
instance, if you wanted to define a function that returns the sum of
squares of the lengths of the strings in a list, you could do so by
combining the helpers :py:func:`~pointfree.pfmap` and
:py:func:`~pointfree.pfreduce`::

    >>> from pointfree import *
    >>> from operator import add
    
    >>> fn = pfmap(len) >> pfmap(lambda n: n**2) >> pfreduce(add, initial=0)
    >>> fn(["foo", "barr", "bazzz"])
    50

Aside from the built-in helpers, you can define your own composable
functions by applying :py:class:`~pointfree.pointfree` as a decorator.
Building upon an example from Beazley's presentation, suppose you have
defined the following functions for operating on lines of text::

    >>> import re
    
    >>> @pointfree
    ... def gen_grep(pat, lines):
    ...     patc = re.compile(pat)
    ...     for line in lines:
    ...         if patc.search(line):
    ...             yield line
    
    >>> @pointfree
    ... def gen_repeat(times, lines):
    ...     for line in lines:
    ...         for n in range(times):
    ...             yield line

    >>> @pointfree
    ... def gen_upcase(lines):
    ...	    for line in lines:
    ...         yield line.upper()
    
And you have some text too::

    >>> bad_poetry = \
    ... """roses are red
    ... violets are blue
    ... I like generators
    ... and this isn't a poem
    ... um let's see...
    ... oh yeah and daffodils are flowers too""".split("\n")

Now say you want to find just the lines of your text that contain the name
of a flower and print them, twice, in upper case.  (A common problem, I'm
sure.)  The given functions can be combined to do so as follows, using
:py:class:`pointfree's <pointfree.pointfree>` automatic partial application
and its function composition operators::

    >>> f = gen_grep(r'(roses|violets|daffodils)') \
    ...     >> gen_upcase \
    ...     >> gen_repeat(2) \
    ...     >> pfprint_all
    
    >>> f(bad_poetry)
    ROSES ARE RED
    ROSES ARE RED
    VIOLETS ARE BLUE
    VIOLETS ARE BLUE
    OH YEAH AND DAFFODILS ARE FLOWERS TOO
    OH YEAH AND DAFFODILS ARE FLOWERS TOO

In addition to the ``>>`` operator for "forward" composition (borrowed from
F#), functions can also be composed with the ``*`` operator, which is
intended to be remniscent of the circle operator "∘" from algebra, or the
corresponding dot operator in Haskell::

    >>> @pointfree
    ... def f(x):
    ...     return x**2
    
    >>> @pointfree
    ... def g(x):
    ...     return x+1
    
    >>> h = f * g
    >>> h(2)
    9

Of course you don't have to define your methods using decorator notation in
order to use :py:class:`~pointfree.pointfree`; you can directly instantiate
the class from an existing function or method::

    >>> (pf(lambda x: x*2) * pf(lambda x: x+1))(3)
    8

(``pf`` is provided as a shorthand alias for the
:py:class:`~pointfree.pointfree` class.)

If you want automatic partial application but not the composition
operators, use the module's :py:class:`~pointfree.partial` decorator
instead::

    >>> @partial
    ... def add_three(a, b, c):
    ...     return a + b + c
    
    >>> add_three(1)(2)(3)
    6

The module's partial application support has some subtle intentional
differences from normal Python function application rules.  Please see the
:ref:`module reference <module_reference>` for details.


Getting the module
------------------

Full documentation is available on the web at:

http://markshroyer.com/docs/pointfree/latest/

The easiest way to install the latest release on your machine is to get it
from PyPI_ using pip_::

    $ pip install pointfree

or easy_install::

    $ easy_install pointfree

.. _PyPI: https://pypi.python.org/

.. _pip: http://pypi.python.org/pypi/pip

Or you can `download the module manually
<https://pypi.python.org/pypi/pointfree/>`_ and perform the standard
distutils incantations::

    $ tar xzf pointfree-*.tar.gz
    $ cd pointfree-*
    $ python setup.py install

The module's development repository is hosted on Github:

https://github.com/markshroyer/pointfree

and the very latest development version can also be installed using pip::

    $ pip install git+git://github.com/markshroyer/pointfree.git

:py:mod:`pointfree` is compatible with the following Python
implementations:

* CPython 2.6, 2.7, 3.0, 3.1, and 3.2

* PyPy 1.6.0

* IronPython 2.7.1

Python 3 is fully supported, including `PEP 3102`_ keyword-only arguments.

.. _`PEP 3102`: http://www.python.org/dev/peps/pep-3102/
