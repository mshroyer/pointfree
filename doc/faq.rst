FAQ
===

* **Q. Python already includes a partial application class in the standard
  library's functools module; why not just use that?**

  There are two major reasons that I felt the need to write a new
  implementation of partial function application for this module.

  First, use of the function composition operators provided by the
  :py:class:`~pointfree.pointfree` decorator requires cooperation between
  the partial application mechanism and the implementation of overloaded
  operators; the result of a partial application must be an object which
  defines the necessary operators, so at the very least I would need to
  wrap :py:func:`functools.partial` anyway.  (And that in itself would not
  be easy, because :py:func:`functools.partial` does not provide a way to
  test whether enough arguments have been provided to call the underlying
  function.)

  The second reason is a subjective matter of taste.  The standard
  library's :py:func:`~functools.partial` requires explicit creation of a
  new object every time you wish to perform partial application and then a
  separate call in order to actually invoke the underlying function, and
  this is more verbose and (in my opinion) less elegant than I would like.
  For a contrived example::

      >>> from functools import partial
              
      >>> def add_thrice(a, b, c):
      ...     return a + b + c
      
      >>> plusone = partial(add_thrice, 1)
      >>> plusone(2, 3)
      6
      >>> plusthree = partial(plusone, 2)
      >>> plusthree(3)
      6

  In contrast, pointfree's :py:class:`~pointfree.partial` decorator lets
  you perform partial application with the same syntax as "full"
  application::

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

  There are also several minor ways in which :py:func:`functools.partial`
  is not ideal for supporting the pointfree style.  If you have a function
  of two arguments and you specify the first as a keyword argument, you
  cannot then specify the second positionally in a subsequent application;
  this would prevent such a partially-applied function from being composed
  with other functions::

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
  in the :ref:`module_reference`)::

      >>> from pointfree import partial
      
      >>> @partial
      ... def add(a, b):
      ...     return a + b
      
      >>> p = add(a=1)
      >>> p(2)
      3

  Also, with the standard library's partial class you don't see errors
  immediately when you apply invalid positional or keyword arguments; the
  exception is only raised when you later ``__call__`` the partial object::

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

* **Q. Are there any disadvantages to pointfree's partial application
  style?**

  Because Python does not currently expose built-in functions for
  introspection, the pure-Python :py:class:`pointfree.partial` wrapper does
  not work with built-in functions.

  Also, with the pointfree implementation of partial application you cannot
  specify optional positional arguments in *multiple* applications, because
  evaluation will occur automatically as soon as enough arguments have been
  specified.  So, for instance, with :py:func:`functools.partial`::

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
      
      >>> partial(add_all)(1, 2) # evaluated immediately
      3

  Despite these limitations, I prefer the brevity of the pointfree
  implementation (which is of course why I wrote it).  Naturally, your
  mileage may vary.
