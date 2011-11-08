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

__all__     = ['partial', 'pointfree', 'ignore', 'printfn']

import sys, inspect, types

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

    def __init__(self, f, argv={}, copy_sig=None):
        self.f = f
        self.argv = argv.copy()
        self.__call_error = None

        if copy_sig is not None:
            self.pargl     = list(copy_sig.pargl)
            self.kargl     = list(copy_sig.kargl)
            self.def_argv  = copy_sig.def_argv.copy()
            self.var_pargs = copy_sig.var_pargs
            self.var_kargs = copy_sig.var_kargs

        elif isinstance(f, classmethod) or isinstance(f, staticmethod):
            self.__call_error = "'%s' object is not callable" % type(f).__name__

        else:
            # Extract function signature, default arguments, keyword-only
            # arguments, and whether or not variable positional or keyword
            # arguments are allowed.  This also supports calling unbound
            # instance methods by passing an object instance as the first
            # argument; however, unbound classmethod and staticmethod
            # objects are not callable, so we do not attempt to support
            # them here.

            if isinstance(f, types.MethodType):
                # A bound instance or class method.
                argspec = getfullargspec(f.__func__)
                self.pargl = argspec[0][1:]
            else:
                # A regular function, an unbound instance method, or a
                # bound static method.
                argspec = getfullargspec(f)
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

        self.__doc__  = f.__doc__  if hasattr(f, '__doc__')  else ''
        self.__name__ = f.__name__ if hasattr(f, '__name__') else '<unnamed>'

    def __get__(self, inst, owner=None):
        return self.__class__(self.f.__get__(inst, owner))

    def __call__(self, *new_pargs, **new_kargs):
        if self.__call_error:
            raise TypeError(self.__call_error)

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
            return self.f(*fpargs, **fkargs)
        else:
            return self.__class__(self.f, argv=new_argv, copy_sig=self)

class pointfree(partial):
    """Decorator for function composition operators

    Converts a Python function or method into one supporting composition
    via the * and >> operators.  Pointfree objects also support automatic
    partial application (see the partial class, above).

    """

    def __mul__(self, g):
        return self.__class__(lambda *p,**k: self(g.f(*p,**k)), argv=g.argv, copy_sig=g)

    def __rshift__(self, g):
        return self.__class__(lambda *p,**k: g(self.f(*p,**k)), argv=self.argv, copy_sig=self)

@pointfree
def ignore(iterator):
    for x in iterator: pass

@pointfree
def printfn(output):
    for item in output:
        print(item)
