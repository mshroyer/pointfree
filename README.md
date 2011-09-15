Introduction
============

pointfree is a tiny Python module that makes certain functional programming
constructs easier to use in the Python language.  Included is support for
function "currying" and chained composition using overloaded operators, and
some small utility functions for dealing with iterators.

The goal is to provide support for
[pointfree programming style](http://www.haskell.org/haskellwiki/Pointfree)
in a lightweight manner.


Examples
========

*TODO*


FAQ
===

  - **Q. Python already includes a `partial` class in the standard
    library's functools module; why not just use that?**

    A. In order for both function currying and composition to be supported
    in this fashion, the partial function converter must be aware of the
    composition wrapper class, and return objects wrapped in its type.

    In addition, the standard library's `partial` class requires functions
    to explicitly be partially applied, which is more verbose than I like,
    e.g.:

        def add(a, b):
            return a + b

        plusone = functools.partial(add, 1)

    whereas with the pointfree module you can instead do:

        @curryable
        def add(a, b):
            return a + b

        plusone = add(1)

    Part of the advantage of writing in the pointfree style is that it can
    be a very clean and elegant way of expressing certain types of
    computations.  I feel that having to explicitly perform partial
    application detracts from this.

  - **Q. Why aren't keyword arguments supported?**

    A. I just haven't gotten around putting in keyword argument support,
    feel free to give it a try if you're interested, and then send me a
    pull request.

Author
======

Mark Shroyer <code@markshroyer.com>

Find the latest version at: http://github.com/markshroyer/python-pointfree
