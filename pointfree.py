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
            argspec = inspect.getargspec(f.__func__)
        else:
            argspec = inspect.getargspec(f)

        if isinstance(f, types.MethodType):
            self.args = (argspec[0])[1:]
        else:
            self.args = (argspec[0])[:]

        self.var_args  = argspec[1] is not None
        self.var_kargs = argspec[2] is not None
        self.defaults  = argspec[3] if argspec[3] is not None else ()

        if hasattr(f, '__doc__'):
            self.__doc__ = f.__doc__
        if hasattr(f, '__name__'):
            self.__name__ = f.__name__

    def __get__(self, inst, owner=None):
        if hasattr(self.f, '__call__'):
            # Bind instance method
            return self.__class__(types.MethodType(self.f, inst), argvals=self.argvals)
        else:
            # Bind class or static method
            return self.__class__(self.f.__get__(None, owner), argvals=self.argvals)

    def __call__(self, *apply_av, **apply_kav):
        new_argvals = self.argvals.copy()
        extra_argvals = []

        for v in apply_av:
            arg_i = None
            for name in self.args:
                if not new_argvals.has_key(name):
                    arg_i = name
                    break

            if arg_i:
                new_argvals[arg_i] = v
            else:
                extra_argvals.append(v)

        for k,v in apply_kav.iteritems():
            if not (self.var_kargs or (k in self.args)):
                raise TypeError("%s() got an unexpected keyword argument '%s'" % (self.__name__, k))
            new_argvals[k] = v

        numd = len(self.defaults) if self.defaults else 0
        mandargs = self.args if numd == 0 else self.args[:-numd]
        fully_applied = True
        for name in mandargs:
            if not new_argvals.has_key(name):
                fully_applied = False
                break

        if fully_applied:
            fargs  = [new_argvals[n] for n in self.args if new_argvals.has_key(n)] + extra_argvals
            fkargs = dict((key,val) for key,val in new_argvals.iteritems() if not (key in self.args))
            return self.f(*fargs, **fkargs)
        else:
            return self.__class__(self.f, argvals=new_argvals)

class pointfree(partial):
    """@pointfree function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.  Functions with
    this decorator also automatically support partial application.

    """

    def __mul__(self, g):
        instance = self.__class__(lambda *a: self(g(*a)))
        if hasattr(g, 'argc'):
            instance.args = g.args
        return instance

    def __rshift__(self, g):
        instance = self.__class__(lambda *a: g(self(*a)))
        instance.args = self.args
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
