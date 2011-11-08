Introduction
------------

pointfree is a small module that makes certain functional programming
constructs more convenient to use in the Python language.

Specifically, it provides:

* A decorator to enable *automatic* partial application of functions and
  methods.
* Notations for function composition through operator overloading.
* Helper functions to make composing generators more elegant.

The objective is to support the `pointfree programming style
<http://www.haskell.org/haskellwiki/Pointfree>`_ in a lightweight and easy
to use manner -- and in particular, to serve as a more convenient syntax
for the kind of generator chaining described in David Beazley's PyCon 2008
presentation, `"Generator Tricks for Systems Programmers"
<http://www.dabeaz.com/generators/Generators.pdf>`_.


Examples
--------

pointfree's ``partial`` decorator lets you create functions and methods
that support automatic partial application.  This means that you can do the
following::

    >>> from pointfree import *
    
    >>> @partial
    ... def adder(a,b,c):
    ...     return a + 2*b + 3*c
    
    >>> adder(1,2,3)
    14
    >>> adder(1)(2)(3)
    14

Keyword arguments are fully supported (including PEP 3102 keyword-only
arguments on Python 3).  However, note that there are some subtle
differences from standard Python function application in how keyword and
positional arguments are mixed together; please refer to the API reference
for full details::

    >>> adder(a=1,b=2,c=3)
    14
    >>> adder(1)(2,c=3)
    14

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
  necessary operators, so at the very least I would need to wrap the
  standard library ``partial`` anyway.

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

* **Q. OK, so what are the disadvantages to pointfree's partial
  decorator?**

  *TODO*


Author
------

By `Mark Shroyer <http://markshroyer.com/>`_.
