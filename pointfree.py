"""
python-pointfree: Pointfree style support for Python

https://github.com/markshroyer/python-pointfree

Pointfree provides support for the point-free programming style in Python.
It works in CPython versions 2.6, 2.7, 3.0, 3.1, and 3.2, as well as PyPy
1.6.0 and IronPython 2.7.1.  In Python 3, keyword-only arguments are fully
supported.

See the documentation for the partial and pointfree classes, below, for
details on usage.

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

"""

from __future__ import print_function

__author__  = "Mark Shroyer"
__email__   = "code@markshroyer.com"
__version__ = 0.1

__all__ = [
    'partial',
    'pointfree',
    'pfmap',
    'pfreduce',
    'pfprint_all',
    'pfignore_all',
    ]

import sys, inspect, types, itertools

# No getfullargspec in Python 2, since there are no keyword-only arguments.
if hasattr(inspect, 'getfullargspec'):
    from inspect import getfullargspec
else:
    def getfullargspec(f):
        return inspect.getargspec(f) + ([], None, {})

class partial(object):
    """Decorator for automatic partial application

    Converts a regular Python function or method into one supporting
    automatic partial application.

    >>> @partial
    ... def foo(a,b,c):
    ...     return a + b + c
    >>> foo(1,2,3)
    6
    >>> foo(1)(2)(3)
    6

    Arguments can be grouped in any combination:

    >>> foo(1,2)(3)
    6
    >>> foo(1)(2,3)
    6

    Generally speaking, the evaluation strategy is to apply all supplied
    arguments to the underlying function as soon as possible.

    """

    def __init__(self, func, *pargs, **kargs):
        self.func = func
        self.argv = {}
        self.__call_error = None

        if isinstance(func, classmethod) or isinstance(func, staticmethod):
            self.__call_error = "'%s' object is not callable" % type(func).__name__

        else:
            # Extract function signature, default arguments, keyword-only
            # arguments, and whether or not variable positional or keyword
            # arguments are allowed.  This also supports calling unbound
            # instance methods by passing an object instance as the first
            # argument; however, unbound classmethod and staticmethod
            # objects are not callable, so we do not attempt to support
            # them here.

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

        self.__doc__  = func.__doc__  if hasattr(func, '__doc__')  else ''
        self.__name__ = func.__name__ if hasattr(func, '__name__') else '<unnamed>'

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

        dest               = klass(func or inst.func)
        dest.argv          = (argv or inst.argv).copy()
        #dest.extra_argv    = list(extra_argv if extra_argv else inst.extra_argv)

        if copy_sig:
            dest.pargl     = list(inst.pargl)
            dest.kargl     = list(inst.kargl)
            dest.def_argv  = inst.def_argv.copy()
            dest.var_pargs = inst.var_pargs
            dest.var_kargs = inst.var_kargs

        return dest

    def __get__(self, inst, owner=None):
        return self.make_copy(self, func=self.func.__get__(inst, owner), copy_sig=False)

    def __new_argv(self, *new_pargs, **new_kargs):
        new_argv = self.argv.copy()
        extra_argv = []

        for v in new_pargs:
            arg_name = None
            for name in self.pargl:
                if not name in new_argv:
                    arg_name = name
                    break

            if arg_name:
                new_argv[arg_name] = v
            elif self.var_pargs:
                extra_argv.append(v)
            else:
                num_prev_pargs = len([name for name in self.pargl if name in self.argv])
                raise TypeError("%s() takes exactly %d positional arguments (%d given)" \
                                    % (self.__name__, len(self.pargl), num_prev_pargs + len(new_pargs)))

        for k,v in new_kargs.items():
            if not (self.var_kargs or (k in self.pargl) or (k in self.kargl)):
                raise TypeError("%s() got an unexpected keyword argument '%s'" \
                                    % (self.__name__, k))
            new_argv[k] = v

        return (new_argv, extra_argv)

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
    """Decorator for function composition operators

    Converts a Python function or method into one supporting composition
    via the * and >> operators.  Pointfree objects also support automatic
    partial application (see the partial class, above).

    """

    def __mul__(self, g):
        return self.make_copy(g, func=lambda *p,**k: self(g.func(*p,**k)))

    def __rshift__(self, g):
        return self.make_copy(self, func=lambda *p,**k: g(self.func(*p,**k)))

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
    """A pointfree reduce function: Applies a function of two arguments
    cumulatively to the items supplied by the given iterable, so as to
    reduce the iterable to a single value.  If an initial value is
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

    iterator = iterable.__iter__()
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
def pfprint_all(iterator):
    """Pointfree function to print all items from an iterator

    A helper function to 

    """

    for item in iterator:
        print(item)

@pointfree
def pfignore_all(iterator):
    for item in iterator:
        pass
