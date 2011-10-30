"""
Point-free style support for Python

Implements easy function composition and currying via operator overloads
and some trickery using decorators.  This makes it possible to do things
like:

    @curryable
    def add(a, b):
        return a + b

    @curryable
    def mult(a, b):
        return a * b

    # Function currying
    x = add(3)(5)
    f = mult(3)
    y = f(5)
    print (x, y) # prints (8, 15)

    # Currying and forward composition with the >> operator
    g = add(1) >> mult(9) >> add(6)

    # Regular function composition with the * operator
    h = printfn * g
    h(3) # prints 4

This syntax also works with generators, so that you can set up generator
pipelines with the >> operator.  See examples.py, distributed with this
module, for more examples.

https://github.com/markshroyer/python-pointfree

"""

__author__  = "Mark Shroyer"
__email__   = "code@markshroyer.com"
__version__ = 0.1

import inspect, types

class partial(object):
    """@partial function decorator

    Converts a regular Python function into one supporting a form of
    partial application.  Supports positional arguments only.

    """

    def __init__(self, f):
        self.f = f

        if isinstance(f, types.MethodType) or isinstance(f, classmethod):
            self.argc = len(inspect.getargspec(f.__func__)[0]) - 1
        elif isinstance(f, staticmethod):
            self.argc = len(inspect.getargspec(f.__func__)[0])
        else:
            self.argc = len(inspect.getargspec(f)[0])
        self.acum = []

        if hasattr(f, '__doc__'):
            self.__doc__ = f.__doc__
        if hasattr(f, '__name__'):
            self.__name__ = f.__name__

    def __get__(self, inst, owner=None):
        if hasattr(self.f, '__call__'):
            # Instance method
            return self.__class__(types.MethodType(self.f, inst))
        else:
            # Class or static method
            return self.__class__(self.f.__get__(None, owner))

    def __call__(self, *a):
        if len(a) < self.argc:
            thunk = self.__class__(self.f)
            thunk.argc = self.argc - len(a)
            thunk.acum = self.acum + list(a)
            return thunk
        else:
            return apply(self.f, self.acum + list(a))

class pointfree(partial):
    """@pointfree function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.  Functions with
    this decorator also automatically support partial application.

    """

    def __mul__(self, g):
        instance = self.__class__(lambda *a: self(g(*a)))
        instance.argc = g.argc
        return instance

    def __rshift__(self, g):
        instance = self.__class__(lambda *a: g(self(*a)))
        instance.argc = self.argc
        return instance

@pointfree
def ignore(iterator):
    for x in iterator: pass

@pointfree
def printf(output):
    print output,

@pointfree
def printfn(output):
    print output
