Introduction
------------

``pointfree`` is a small module that makes certain functional
programming constructs more convenient to use in Python.

Specifically, it provides:

* A decorator to enable *automatic* partial application of functions and
  methods.
* Notations for function composition through operator overloading.
* Helper functions to make composing generators more elegant.

The objective is to support the `pointfree programming style
<http://www.haskell.org/haskellwiki/Pointfree>`_ in a lightweight and easy
to use manner -- and in particular, to serve as a nice syntax for the kind
of generator chaining described in David Beazley's PyCon 2008 presentation,
`"Generator Tricks for Systems Programmers"
<http://www.dabeaz.com/generators/Generators.pdf>`_.


Examples
--------

The :py:class:`~pointfree.pointfree` decorator lets you partially apply and
compose functions, including generator functions.  Building upon an example
from Beazley's presentation, suppose you have the following functions for
operating on lines of text::

    >>> from pointfree import *
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

Now suppose you want to find just the lines of your text that contain the
name of a flower and print them, twice, in upper case.  The given functions
can be combined to do so as follows, using pointfree's automatic partial
application and function composition operators::

    >>> f = gen_grep(r'(roses|violets|daffodils)') \
    ...     >> gen_upcase \
    ...     >> gen_repeat(2) \
    ...     >> printfn
    
    >>> f(bad_poetry)
    ROSES ARE RED
    ROSES ARE RED
    VIOLETS ARE BLUE
    VIOLETS ARE BLUE
    OH YEAH AND DAFFODILS ARE FLOWERS TOO
    OH YEAH AND DAFFODILS ARE FLOWERS TOO

In addition to the ``>>`` operator for "forward" composition, functions can
also be composed with the ``*`` operator.  (This is intended to be
remniscent of the circle operator "∘" from algebra.)::

    >>> @pointfree
    ... def f(x):
    ...     return x**2
    
    >>> @pointfree
    ... def g(x):
    ...     return x+1
    
    >>> h = f * g
    >>> h(2)
    9

And of course you don't have to define your methods using decorator
notation in order to use :py:class:`~pointfree.pointfree`; you can directly
instantiate the class from an existing function or method::

    >>> (pointfree(lambda x: x*2) * pointfree(lambda x: x+1))(3)
    8

If you want to use automatic partial application but not the composition
operators, you can use the module's :py:class:`~pointfree.partial`
decorator instead::

    >>> @partial
    ... def add_three(a, b, c):
    ...     return a + b + c
    
    >>> add_three(1)(2)(3)
    6

(Using the :py:class:`~pointfree.pointfree` decorator imbues a superset of
the capabilities provided by :py:class:`~pointfree.partial`.)

pointfree's partial application support has some intentional differences
from normal Python function application semantics.  Please refer to the API
reference for details.
