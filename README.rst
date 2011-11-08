Introduction
------------

pointfree is a small module that makes certain functional programming
constructs more convenient to use in Python.

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

The ``pointfree`` decorator lets you partially apply and compose functions,
including generator functions.  Building upon an example from Beazley's
presentation, suppose you have the following functions for operating on
lines of text::

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
notation in order to use pointfree's features; you can directly instantiate
the class from an existing function or method::

    >>> (pointfree(lambda x: x*2) * pointfree(lambda x: x+1))(3)
    8

If you want to use pointfree's automatic partial application support but
not the composition operators, you can use the ``@partial`` decorator
instead::

    >>> @partial
    ... def add_three(a, b, c):
    ...     return a + b + c
    
    >>> add_three(1)(2)(3)
    6

(Using the ``@pointfree`` decorator imbues a superset of the capabilities
provided by ``@partial``.)

pointfree's partial application support has some intentional differences
from normal Python function application semantics.  Please refer to the API
reference for details.


FAQ
---

* **Q. Python already includes a partial application class in the standard
  library's functools module; why not just use that?**

  There are two major reasons that I felt the need to write a new
  implementation of partial function application for this module.

  First, use of the function composition operators provided by the
  ``pointfree`` decorator requires cooperation between the partial
  application mechanism and the implementation of overloaded operators; the
  result of a partial application must be an object which defines the
  necessary operators, so at the very least I would need to wrap
  :py:class:`functools.partial` anyway.

  The second reason is a matter of subjective taste.  The standard
  library's ``partial`` class requires explicit creation of a new object
  every time you wish to perform partial application and then a separate
  call in order to actually invoke the underlying function, and this is
  more verbose and (in my opinion) less elegant than I would like.  For a
  contrived example::

      >>> from functools import partial
              
      >>> def add_thrice(a, b, c):
      ...     return a + b + c
      
      >>> plusone = partial(add_thrice, 1)
      >>> plusone(2, 3)
      6
      >>> plusthree = partial(plusone, 2)
      >>> plusthree(3)
      6

  In contrast, pointfree's ``partial`` decorator lets you perform partial
  application with the same syntax as "full" application::

      >>> from pointfree import partial
      
      >>> @partial
      ... def add_thrice(a, b, c):
      ...     return a + b + c
      
      >>> plusone = add_thrice(1)
      >>> plusone(2, 3)
      6
      >>> plusthree = plusone(2)
      >>> plusthree(3)
      6

  There are also several minor ways in which the functools ``partial``
  object is not ideal for supporting the pointfree style.  If you have a
  function of two arguments and you specify the first as a keyword
  argument, you cannot then specify the second positionally in a subsequent
  application; this would prevent such a partially-applied function from
  being composed with other functions::

      >>> from functools import partial
      
      >>> def add(a, b):
      ...     return a + b
      
      >>> p = partial(add, a=1)
      >>> p(2)
      Traceback (most recent call last):
          ...
      TypeError: add() got multiple values for keyword argument 'a'

  Whereas you can do this with pointfree, due to its slightly different
  semantics for positional argument application (which is fully described
  in the decorator's API reference)::

      >>> from pointfree import partial
      
      >>> @partial
      ... def add(a, b):
      ...     return a + b
      
      >>> p = add(a=1)
      >>> p(2)
      3

  Also, with the standard library's partial class you don't see errors
  immediately when you apply invalid positional or keyword arguments; the
  exception is only raised when you then ``__call__`` the partial object::

      >>> from functools import partial
      
      >>> def add(a, b):
      ...     return a + b
      
      >>> p = partial(add, c=3) # No error is raised yet
      >>> q = partial(p, 1)     # Still no error
      >>> q(2)                  # Now we get an error!
      Traceback (most recent call last):
          ...
      TypeError: add() got an unexpected keyword argument 'c'

  But with pointfree's partial application, the error is raised
  immediately::

      >>> from pointfree import partial
      
      >>> @partial
      ... def add(a, b):
      ...     return a + b
      
      >>> p = add(c=3)
      Traceback (most recent call last):
          ...
      TypeError: add() got an unexpected keyword argument 'c'

* **Q. OK, so what are the disadvantages of pointfree's partial
  decorator?**

  pointfree's ``partial`` implementation does not work on CPython's builtin
  functions::

      >>> from pointfree import partial
      
      >>> partial(pow)(y=3)
      Traceback (most recent call last):
          ...
      TypeError: <built-in function pow> is not a Python function

  Also, with the pointfree implementation you cannot specify optional
  positional arguments in *multiple* applications, because evaluation will
  occur automatically as soon as enough arguments have been specified.  So,
  for instance, with functools ``partial``::

      >>> from functools import partial
      
      >>> def add_all(*argv):
      ...     return sum(argv)
      
      >>> f = partial(add_all, 1, 2)
      >>> g = partial(f, 3, 4)
      >>> g(5)
      15

  Whereas with pointfree, the function would be evaluated as soon as it has
  been supplied any arguments::

      >>> from pointfree import partial
      
      >>> partial(add_all)(1, 2)
      3

  Despite these limitations, I prefer the brevity of the pointfree
  implementation (which is of course why I wrote it).  Naturally, your
  mileage may vary.


Author
------

By `Mark Shroyer <http://markshroyer.com/>`_.
