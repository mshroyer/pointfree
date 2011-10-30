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

class composable(object):
    """@composable function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.

    """

    def __init__(self, f):
        self.f = f

    def __mul__(self, g):
        return self.__class__(lambda *a: self(g(*a)))

    def __rshift__(self, g):
        return self.__class__(lambda *a: g(self(*a)))

    def __get__(self, inst, owner=None):
        if hasattr(self.f, '__call__'):
            # Instance method
            argc = len(inspect.getargspec(self.f)[0]) - 1
            instance = self.__class__(types.MethodType(self.f, inst))
            instance.argc = argc
            return instance
        else:
            # Class or static method
            diff = 1 if isinstance(self.f, classmethod) else 0
            argc = len(inspect.getargspec(self.f.__func__)[0]) - diff
            instance = self.__class__(self.f.__get__(None, owner))
            instance.argc = argc
            return instance

    def __call__(self, *a):
        return self.f(*a)

def compv(val):
    """Turn a non-callable value into a composable function

    Makes a composable function that returns the given value when called.

    """

    return Comp(lambda *a: val)

class currying(composable):
    """@curryable function decorator

    Converts a regular Python function into one supporting a form of
    partial application.  Supports positional arguments only.  Functions
    with this decorator are automatically composable.

    """

    def __call__(self, *a):
        argc = self.argc if hasattr(self, 'argc') else len(inspect.getargspec(self.f)[0])
        acum = self.acum if hasattr(self, 'acum') else []
        #import pdb; pdb.set_trace()
        if len(a) < argc:
            thunk = self.__class__(self.f)
            thunk.argc = argc - len(a)
            thunk.acum = acum + list(a)
            return thunk
        else:
            return apply(self.f, acum + list(a))

@composable
def ignore(iterator):
    for x in iterator: pass

@composable
def printf(output):
    print output,

@composable
def printfn(output):
    print output
