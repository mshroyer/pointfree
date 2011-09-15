"""
fpkit

Functional programming toolkit for Python.

"""

__author__  = "Mark Shroyer"
__email__   = "code@markshroyer.com"
__version__ = 0.1

import inspect

class Comp:
    """@composable function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.

    """

    def __init__(self, f):
        self.f = f

    def __mul__(self, g):
        return self.__class__(lambda *a: self.f(g(*a)))

    def __rshift__(self, g):
        return self.__class__(lambda *a: g(self.f(*a)))

    def __call__(self, *a):
        return self.f(*a)

def compval(val):
    """Turn a non-callable value into a composable function

    Makes a composable function that returns the given value when called.

    """

    return Comp(lambda *a: val)

def curr(f):
    """@curryable function decorator

    Converts a regular Python function into one supporting a form of
    partial application.  Supports positional arguments only.  Functions
    with this decorator are automatically composable.

    """

    def thunk(f, n, acum):
        if n <= 0:
            return f(*acum)
        else:
            return Comp(lambda *a: thunk(f, n-len(a), acum+list(a)))
    return Comp(thunk(f, len(inspect.getargspec(f)[0]), []))

# Verbose form for function decorators
composable = Comp
curryable = curr
