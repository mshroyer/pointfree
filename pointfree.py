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

    def __init__(self, f, argvals={}):
        self.f = f
        self.argvals = argvals

        if isinstance(f, types.MethodType) \
                or isinstance(f, classmethod) \
                or isinstance(f, staticmethod):
            actual_func = f.__func__
        else:
            actual_func = f

        if isinstance(f, types.MethodType):
            self.argspec = (inspect.getargspec(actual_func)[0])[1:]
        else:
            self.argspec = (inspect.getargspec(actual_func)[0])[:]

        self.defaults = inspect.getargspec(actual_func)[3]
        if self.defaults is None: self.defaults = ()

        if hasattr(f, '__doc__'):
            self.__doc__ = f.__doc__
        if hasattr(f, '__name__'):
            self.__name__ = f.__name__

    def is_fully_applied(self):
        numd = len(self.defaults) if self.defaults else 0
        mandargs = self.argspec if numd == 0 else self.argspec[:-numd]
        for arg in mandargs:
            if not self.argvals.has_key(arg):
                return False
        return True

    def next_unapplied_arg(self):
        for arg in self.argspec:
            if not self.argvals.has_key(arg):
                return arg

    def __get__(self, inst, owner=None):
        if hasattr(self.f, '__call__'):
            # Bind instance method
            return self.__class__(types.MethodType(self.f, inst), argvals=self.argvals)
        else:
            # Bind class or static method
            return self.__class__(self.f.__get__(None, owner), argvals=self.argvals)

    def __call__(self, *av, **kav):
        if self.is_fully_applied():
            return self.f(**self.argvals)

        new_argvals = self.argvals.copy()
        if len(av) > 0:
            new_argvals[self.next_unapplied_arg()] = av[0]
            return self.__class__(self.f, argvals=new_argvals)(*(av[1:]), **kav)
        elif len(kav) > 0:
            first_key = kav.keys()[0]
            new_argvals[first_key] = kav[first_key]
            new_kav = kav.copy()
            del new_kav[first_key]
            return self.__class__(self.f, argvals=new_argvals)(*av, **new_kav)
        else:
            return self

class pointfree(partial):
    """@pointfree function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.  Functions with
    this decorator also automatically support partial application.

    """

    def __mul__(self, g):
        instance = self.__class__(lambda *a: self(g(*a)))
        if hasattr(g, 'argc'):
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
