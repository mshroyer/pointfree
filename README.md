Introduction
============

pointfree is a small Python module that makes certain functional
programming constructs easier to use in the Python language.

Specifically, it provides:

  * A decorator to enable automatic partial application of functions and
    methods.
  * Notations for function composition through operator overloading.
  * Helper functions to make composing generators more convenient.

The objective is to support the
[pointfree programming style](http://www.haskell.org/haskellwiki/Pointfree)
in a lightweight and easy to use manner.


Examples
========

*TODO*


Overview
========

Partial application
-------------------

Partial function and method application is enabled with the `@partial`
decorator:

    @partial
    def add(a, b, c):
        return a + b + c
	
    >>> add(1,2,3)
    6
    >>> add(1)(2)(3)
    6
    >>> add(1)(2,3)
    6

Partial application can also be used with methods (including class methods
and static methods), as long as you're using new-style objects.

    class Foo(object):
        def __init__(self, n):
            self.n = n
	    
        @partial
        def add(self, a, b):
            return self.n + a + b

    >>> f = Foo(1)
    >>> f.add(2)(3)
    6
    
If there are arguments with default values, the rule is that the function
will be evaluated as soon as enough of the arguments have been provided to
perform any evaluation.  So:

    @partial
    def add2(a, b, c=3):
        return a + b + c
	
    >>> add2(1)(2)
    6 # doesn't wait for c to be explicitly supplied
    
However, if you want to specify an explicit value for a default argument,
you can do so by supplying multiple arguments at once:

    >>> add2(1,2,4)
    7
    >>> add2(1)(2,4)
    7


FAQ
===

  - **Q. Python already includes a `partial` class in the standard
    library's functools module; why not just use that?**

    The standard library's `partial` class requires functions to explicitly
    be partially applied, which is more verbose than I personally like,
    e.g.:

        def add(a, b):
            return a + b

        plusone = functools.partial(add, 1)
        plustwo = functools.partial(add, 2)

    whereas with the pointfree module you can instead do:

        @partial
        def add(a, b):
            return a + b

        plusone = add(1)
        plustwo = add(2)

    Part of the advantage of writing in the pointfree style is that it can
    be a very clean and elegant way of expressing certain types of
    computations.  I feel that having to explicitly perform partial
    application detracts from this elegance.


Author
======

By [Mark Shroyer](http://markshroyer.com/) &lt;code@markshroyer.com&gt;

Find the latest version at: http://github.com/markshroyer/python-pointfree
