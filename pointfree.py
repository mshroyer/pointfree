"""
Pythonic pointfree programming.

* Full documentation: http://markshroyer.com/docs/pointfree/latest/
* Project page: https://github.com/markshroyer/pointfree


Copyright notice
----------------

Copyright 2011 Mark Shroyer

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License.  You may obtain a copy
of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
License for the specific language governing permissions and limitations
under the License.


Usage
-----

The general use case is to wrap functions in the
:py:class:`~pointfree.pointfree` wrapper / decorator class, granting them
both automatic partial application support and a pair of function
composition operators::

    >>> from pointfree import *
    
    >>> @pointfree
    ... def pfadd(a, b):
    ...     return a + b

    >>> @pointfree
    ... def pfexp(n, exp):
    ...     return n ** exp
    
    >>> fn = pfexp(exp=2) * pfadd(1)
    >>> fn(3)
    16

:py:class:`pointfree.pointfree` inherits from the
:py:class:`pointfree.partial` class (not to be confused with
:py:func:`functools.partial`), which provides automatic partial application
but not the function composition operators.  See :py:class:`partial's
<pointfree.partial>` documentation for details of the partial application
semantics, and :py:class:`pointfree's <pointfree.pointfree>` documentation
for information about the function composition operators.

The module also includes a number of pre-defined helper functions which can
be combined for various purposes::

    >>> fn = pfmap(lambda x: x**3) >> pfprint_all
    
    >>> fn(range(4))
    0
    1
    8
    27

Refer to the section :ref:`helper_functions` for information about the
helpers provided by this module.

"""

from __future__ import print_function

__author__  = "Mark Shroyer"
__email__   = "code@markshroyer.com"
__version__ = "1.0.0"

__all__ = [
    'partial',
    'pointfree',
    'pf',
    'pfmap',
    'pfreduce',
    'pfcollect',
    'pfprint',
    'pfprint_all',
    'pfignore_all',
    ]

import sys, inspect, types, itertools, functools

# No getfullargspec in Python 2, since there are no keyword-only arguments.
if hasattr(inspect, 'getfullargspec'):
    from inspect import getfullargspec
else:
    def getfullargspec(f):
        return inspect.getargspec(f) + ([], None, {})

class partial(object):
    """Wraps a regular Python function or method into a callable object
    supporting automatic partial application.

    :param func: Function or method to wrap
    :param pargs: Optional, positional arguments for the wrapped function
    :param kargs: Optional, keyword arguments for the wrapped function

    Example::

        >>> @partial
        ... def foo(a,b,c):
        ...     return a + b + c
        >>> foo(1,2,3)
        6
        >>> foo(1)(2)(3)
        6

    Generally speaking, the evaluation strategy with regard to automatic
    partial application is to apply all given arguments to the underlying
    function as soon as possible.

    When a :py:class:`~pointfree.partial` instance is called, the
    positional and keyword arguments supplied are combined with the
    instance's own cache of arguments for the wrapped function (which is
    empty to begin with, for instances directly wrapping -- or applied as
    decorators to -- pure Python functions or methods).  If the combined
    set of arguments is sufficient to invoke the wrapped function, then the
    function is called and its result returned.  If the combined arguments
    are *not* sufficient, then a new copy of the wrapper is returned
    instead, with the new combined argument set in its cache.

    Calling a :py:class:`~pointfree.partial` object never changes its
    state; instances are immutable for practical purposes, so they can be
    called and reused indefinitely::

        >>> p = q = foo(1,2)
        >>> p(3)
        6
        >>> q(4) # Using the same instance twice
        7

    Arguments with default values do not need to be explicitly specified in
    order for evaluation to occur.  In the following example, ``foo2`` can
    be evaluated as soon as we have specified the arguments ``a`` and
    ``b``::

        >>> @partial
        ... def foo2(a, b, c=3):
        ...     return a + b + c

        >>> foo2(1,2)
        6
        >>> foo2(1)(2)
        6

    However, if extra arguments are supplied prior to evaluation, and if
    the underlying function is capable of accepting those arguments, then
    those will be passed to the function as well.  If we call ``foo2`` as
    follows, the third argument will be passed to the wrapped function as
    ``c``, overriding its default value::

        >>> foo2(1,2,5)
        8
        >>> foo2(3)(4,5)
        12

    This works similarly with functions that accept variable positional
    argument lists::

        >>> @partial
        ... def foo3(a, *args):
        ...     return a + sum(args)

        >>> foo3(1)
        1
        >>> foo3(1,2)
        3
        >>> foo3(1,2,3)
        6

    Or variable keyword argument lists::

        >>> @partial
        ... def foo4(a, **kargs):
        ...     kargs.update({'a': a})
        ...     return kargs

        >>> result = foo4(3, b=4, c=5)
        >>> for key in sorted(result.keys()):
        ...     print("%s: %s" % (key, result[key]))
        a: 3
        b: 4
        c: 5

    But if you try to supply an argument that the function cannot accept, a
    :py:exc:`~exceptions.TypeError` will be raised as soon as you attempt
    to do so -- the wrapper doesn't wait until the underlying function is
    called before raising the exception (unlike with
    :py:func:`functools.partial`)::

        >>> @partial
        ... def foo5(a, b, c):
        ...     return a + b + c

        >>> foo5(d=7)
        Traceback (most recent call last):
            ...
        TypeError: foo5() got an unexpected keyword argument 'd'

    There are some sutble differences between how automatic partial
    application works in this module and the semantics of regular Python
    function application (or, again, of :py:func:`functools.partial`).
    First, keyword arguments to partially applied functions can override an
    argument specified in a previous call::

        >>> @partial
        ... def foo6(a, b, c):
        ...     return (a, b, c)

        >>> foo6(1)(b=2)(b=3)(4) # overriding b given as keyword
        (1, 3, 4)
        >>> foo6(1,2)(b=3)(4) # overriding b given positionally
        (1, 3, 4)

    Also, the wrapper somewhat blurs the line between positional and
    keyword arguments for the sake of flexibilty.  If an argument is
    specified with a keyword and then "reached" by a positional argument in
    a subsequent call, the remaining positional argument values "wrap
    around" the argument previously specified as a keyword.

    This second difference is best illustrated by example.  Again using the
    function ``foo6`` from above, if we specify ``b`` as a keyword
    argument::

        >>> p = foo6(b=2)

    and then apply two positional arguments to the resulting
    :py:class:`~pointfree.partial` instance, those arguments will be used
    to specify ``a`` and ``c``, skipping over ``b`` because it has already
    been specified:

        >>> p(1,3)
        (1, 2, 3)

    This approach was chosen because it allows us to compose partial
    applications of functions where a previous argument has been specified
    as a keyword argument.

    As well as functions, :py:class:`~pointfree.partial` can be applied to
    methods, including class and static methods::

        >>> class Foo7(object):
        ...     m = 2
        ...
        ...     def __init__(self, n):
        ...         self.n = n
        ...
        ...     @partial
        ...     def bar_inst(self, a, b, c):
        ...         return self.m + self.n + a + b + c
        ...
        ...     @partial
        ...     @classmethod
        ...     def bar_class(klass, a, b, c):
        ...         return klass.m + a + b + c
        ...
        ...     @partial
        ...     @staticmethod
        ...     def bar_static(a, b, c):
        ...         return a + b + c

        >>> f = Foo7(3)
        >>> f.bar_inst(4)(5)(6)
        20
        >>> f.bar_class(3)(4)(5)
        14
        >>> f.bar_static(2)(3)(4)
        9

    The wrapper can also be instantiated from another
    :py:class:`~pointfree.partial` instance::

        >>> def foo8(a, b, c, *args):
        ...     return a + b + c + sum(args)

        >>> p = partial(foo8, 1)
        >>> q = partial(p, 2)
        >>> q(3)
        6

    Or even from a :py:func:`functools.partial` instance:

        >>> p = functools.partial(foo8, 1)
        >>> q = partial(p)
        >>> q(2)(3)
        6

    However, it cannot currently wrap a Python builtin function (or a
    :py:func:`functools.partial` instance which wraps a builtin function),
    as Python does not currently provide sufficient reflection for its
    builtins.

    While you will probably apply :py:class:`~pointfree.partial` as a
    decorator when defining your own functions, you can also wrap existing
    functions by instantiating the class directly::

        >>> partial(foo8)(1)(2)(3)
        6

    Or like with :py:func:`functools.partial`, you can specify arguments
    for the wrapped function when you instantiate a wrapper:

        >>> p = partial(foo8, 1)
        >>> p(2)(3)
        6

    But unlike calling an existing wrapper instance, the wrapped function
    will not be invoked during instantiation even if enough arguments are
    supplied in order to do so; invocation does not occur until the
    :py:class:`~pointfree.partial` instance is called at least once, even
    with an empty argument list:

        >>> p = partial(foo8, 1, 2, 3)
        >>> type(p)
        <class 'pointfree.partial'>
        >>> p()
        6
        >>> p(4)
        10

    """

    def __init__(self, func, *pargs, **kargs):
        self.func = func
        self.argv = {}
        self.extra_argv = []
        self.__call_error = None

        if isinstance(func, partial):
            self.func = func.func
            functools.update_wrapper(self, self.func)
            inst = func
            self.argv = inst.argv
            self.extra_argv = inst.extra_argv
            self.__sig_from_partial(inst)

        elif isinstance(func, functools.partial):
            self.func = func.func
            functools.update_wrapper(self, self.func)
            self.__sig_from_func(self.func)
            partial_args = func.args or ()
            partial_keywords = func.keywords or {}
            self.__update_argv(*partial_args, **partial_keywords)

        elif isinstance(func, classmethod) or isinstance(func, staticmethod):
            self.__call_error = "'%s' object is not callable" % type(func).__name__

        else:
            functools.update_wrapper(self, func)
            self.__sig_from_func(func)

        self.__update_argv(*pargs, **kargs)

    def __sig_from_func(self, func):
        """Extract function signature, default arguments, keyword-only
        arguments, and whether or not variable positional or keyword
        arguments are allowed.  This also supports calling unbound instance
        methods by passing an object instance as the first argument;
        however, unbound classmethod and staticmethod objects are not
        callable, so we do not attempt to support them here."""

        if isinstance(func, types.MethodType):
            # A bound instance or class method.
            argspec = getfullargspec(func.__func__)
            self.pargl = argspec[0][1:]
        else:
            # A regular function, an unbound instance method, or a
            # bound static method.
            argspec = getfullargspec(func)
            self.pargl = argspec[0][:]

        if argspec[3] is not None:
            def_offset = len(self.pargl) - len(argspec[3])
            self.def_argv = dict((self.pargl[def_offset+i],argspec[3][i]) \
                                     for i in range(len(argspec[3])))
        else:
            self.def_argv = {}

        self.var_pargs = argspec[1] is not None
        self.var_kargs = argspec[2] is not None
        self.kargl     = argspec[4]

        # We need keyword-only arguments' default values too.
        if argspec[5] is not None:
            self.def_argv.update(argspec[5])

    def __sig_from_partial(self, inst):
        """Extract function signature from an existing partial instance."""

        self.pargl     = list(inst.pargl)
        self.kargl     = list(inst.kargl)
        self.def_argv  = inst.def_argv.copy()
        self.var_pargs = inst.var_pargs
        self.var_kargs = inst.var_kargs

    @classmethod
    def make_copy(klass, inst, func=None, argv=None, extra_argv=None, copy_sig=True):
        """Makes a new instance of the partial application wrapper based on
        an existing instance, optionally overriding the original's wrapped
        function and/or saved arguments.

        :param inst: The partial instance we're copying
        :param func: Override the original's wrapped function
        :param argv: Override saved argument values
        :param extra_argv: Override saved extra positional arguments
        :param copy_sig: Copy original's signature?
        :rtype: New partial wrapper instance

        """

        dest            = klass(func or inst.func)
        dest.argv       = (argv or inst.argv).copy()
        dest.extra_argv = list(extra_argv if extra_argv else inst.extra_argv)

        if copy_sig:
            dest.__sig_from_partial(inst)

        return dest

    def __get__(self, inst, owner=None):
        return self.make_copy(self, func=self.func.__get__(inst, owner), copy_sig=False)

    def __new_argv(self, *new_pargs, **new_kargs):
        """Calculate new argv and extra_argv values resulting from adding
        the specified positional and keyword arguments."""

        new_argv = self.argv.copy()
        new_extra_argv = list(self.extra_argv)

        for v in new_pargs:
            arg_name = None
            for name in self.pargl:
                if not name in new_argv:
                    arg_name = name
                    break

            if arg_name:
                new_argv[arg_name] = v
            elif self.var_pargs:
                new_extra_argv.append(v)
            else:
                num_prev_pargs = len([name for name in self.pargl if name in self.argv])
                raise TypeError("%s() takes exactly %d positional arguments (%d given)" \
                                    % (self.__name__,
                                       len(self.pargl),
                                       num_prev_pargs + len(new_pargs)))

        for k,v in new_kargs.items():
            if not (self.var_kargs or (k in self.pargl) or (k in self.kargl)):
                raise TypeError("%s() got an unexpected keyword argument '%s'" \
                                    % (self.__name__, k))
            new_argv[k] = v

        return (new_argv, new_extra_argv)

    def __update_argv(self, *pargs, **kargs):
        self.argv, self.extra_argv = self.__new_argv(*pargs, **kargs)

    def __call__(self, *new_pargs, **new_kargs):
        if self.__call_error:
            raise TypeError(self.__call_error)

        new_argv, extra_argv = self.__new_argv(*new_pargs, **new_kargs)

        applic_argv = self.def_argv.copy()
        applic_argv.update(new_argv)

        applic_ready = True
        for name in self.pargl:
            if not name in applic_argv:
                applic_ready = False
                break

        if applic_ready:
            for name in self.kargl:
                if not name in applic_argv:
                    applic_ready = False
                    break

        if applic_ready:
            fpargs = [new_argv[n] for n in self.pargl if n in new_argv] + extra_argv
            fkargs = dict((n,v) for n,v in new_argv.items() if not n in self.pargl)
            return self.func(*fpargs, **fkargs)
        else:
            return self.make_copy(self, argv=new_argv)

class pointfree(partial):
    """Wraps a regular Python function or method into a callable object
    supporting the ``>>`` and ``*`` function composition operators, as well
    as automatic partial application inherited from
    :py:class:`~pointfree.partial`.

    :param func: Function or method to wrap
    :param pargs: Optional, positional arguments for the wrapped function
    :param kargs: Optional, keyword arguments for the wrapped function

    This class inherits its partial application behavior from
    :py:class:`~pointfree.partial`; refer to its documentation for details.

    On top of automatic partial application, the
    :py:class:`~pointfree.pointfree` wrapper adds two function composition
    operators, ``>>`` and ``*``, for "forward" and "reverse" function
    composition respectively.  For example, given the following wrapped
    functions::

        >>> @pointfree
        ... def pfadd(a, b):
        ...     return a + b

        >>> @pointfree
        ... def pfmul(a, b):
        ...     return a * b

    The following forward composition defines the function ``f()`` as one
    which takes a given number, adds one to it, and then multiplies the
    result of the addition by two::

        >>> f = pfadd(1) >> pfmul(2)
        >>> f(1)
        4

    Reverse composition simply works in the opposite direction.  In this
    example, ``g()`` takes a number, multiplies it by three, and then adds
    four::

        >>> g = pfadd(4) * pfmul(3)
        >>> g(5)
        19

    The alias ``pf`` is provided for :py:class:`~pointfree.pointfree` to
    conserve electrons when wrapping functions inline::

        >>> def add(a, b):
        ...     return a + b

        >>> def mul(a, b):
        ...     return a * b

        >>> f = pf(add, 1) >> pf(mul, 2)
        >>> f(2)
        6

    When using :py:class:`~pointfree.pointfree` as a decorator on class or
    static methods, you must ensure that it is the "topmost" decorator, so
    that the resulting object is a :py:class:`~pointfree.pointfree`
    instance in order for the composition operators to work.

    """

    def __mul__(self, g):
        return self.make_copy(g, func=lambda *p,**k: self(g.func(*p,**k)))

    def __rshift__(self, g):
        return self.make_copy(self, func=lambda *p,**k: g(self.func(*p,**k)))

# Shorthand pointfree notation
pf = pointfree

@pointfree
def pfmap(func, iterable):
    """A pointfree map function: Returns an iterator over the results of
    applying a function of one argument to the items of a given iterable.
    The function is provided "lazily" to the given iterable; each function
    application is performed on the fly as it is requested.

    :param func: A function of one argument to apply to each item
    :param iterable: An iterator yielding input for the function
    :rtype: Iterator of function application results

    Example::

        >>> f = pfmap(lambda x: x+1) \\
        ...     >> pfmap(lambda x: x*2) \\
        ...     >> pfcollect
        
        >>> f(range(5))
        [2, 4, 6, 8, 10]

    """

    for item in iterable:
        yield func(item)

@pointfree
def pfreduce(func, iterable, initial=None):
    """A pointfree reduce / left fold function: Applies a function of two
    arguments cumulatively to the items supplied by the given iterable, so
    as to reduce the iterable to a single value.  If an initial value is
    supplied, it is placed before the items from the iterable in the
    calculation, and serves as the default when the iterable is empty.

    :param func: A function of two arguments
    :param iterable: An iterable yielding input for the function
    :param initial: An optional initial input for the function
    :rtype: Single value

    Example::

        >>> from operator import add
        
        >>> sum_of_squares = pfreduce(add, initial=0) * pfmap(lambda n: n**2)
        >>> sum_of_squares([3, 4, 5, 6])
        86

    """

    iterator = iter(iterable)
    try:
        first_item = next(iterator)
        if initial:
            value = func(initial, first_item)
        else:
            value = first_item
    except StopIteration:
        return initial

    for item in iterator:
        value = func(value, item)
    return value

@pointfree
def pfcollect(iterable, n=None):
    """Collects and returns a list of values from the given iterable.  If
    the n parameter is not specified, collects all values from the
    iterable.

    :param iterable: An iterable yielding values for the list
    :param n: An optional maximum number of items to collect
    :rtype: List of values from the iterable

    Example::

        >>> @pointfree
        ... def fibonaccis():
        ...     a, b = 0, 1
        ...     while True:
        ...         a, b = b, a+b
        ...         yield a

        >>> (pfcollect(n=10) * fibonaccis)()
        [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

    """

    if n:
        return list(itertools.islice(iterable, n))
    else:
        return list(iterable)

@pointfree
def pfprint(item, end='\n', file=None):
    """Prints an item.

    :param item: The item to print
    :param end: String to append to the end of printed output
    :param file: File to which output is printed
    :rtype: None

    Example::

        >>> from operator import add
        
        >>> fn = pfreduce(add, initial=0) >> pfprint
        >>> fn([1, 2, 3, 4])
        10

    """

    # Can't just make sys.stdout the file argument's default value, because
    # then we would be capturing the stdout file descriptor, and then
    # doctest -- which works by redefining sys.stdout -- would fail:
    if file is None:
        file = sys.stdout

    print(item, end=end, file=file)

@pointfree
def pfprint_all(iterable, end='\n', file=None):
    """Prints each item from an iterable.

    :param iterable: An iterable yielding values to print
    :param end: String to append to the end of printed output
    :param file: File to which output is printed
    :rtype: None

    Example::

        >>> @pointfree
        ... def prefix_all(prefix, iterable):
        ...     for item in iterable:
        ...         yield "%s%s" % (prefix, item)

        >>> fn = prefix_all("An item: ") >> pfprint_all

        >>> fn(["foo", "bar", "baz"])
        An item: foo
        An item: bar
        An item: baz

    """

    for item in iterable:
        pfprint(item, end=end, file=file)

@pointfree
def pfignore_all(iterator):
    """Consumes all the items from an iterable, discarding their output.
    This may be useful if evaluating the iterable produces some desirable
    side-effect, but you have no need to collect its output.

    :param iterable: An iterable
    :rtype: None

    Example::

        >>> result = []

        >>> @pointfree
        ... def append_all(collector, iterable):
        ...     for item in iterable:
        ...         collector.append(item)
        ...         yield item

        >>> @pointfree
        ... def square_all(iterable):
        ...     for item in iterable:
        ...         yield item**2

        >>> fn = square_all \\
        ...      >> append_all(result) \\
        ...      >> pfignore_all
        >>> fn([1, 2, 3, 4])
        >>> result
        [1, 4, 9, 16]

    """

    for item in iterator:
        pass
