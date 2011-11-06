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
    """@partial function decorator

    Converts a regular Python function into one supporting a form of
    partial application.  Supports positional arguments only.

    """

    def __init__(self, f, argv={}, copy_sig=None):
        self.f = f
        self.argv = argv.copy()

        if copy_sig is not None:
            # Copy the signature from an existing partial instance.

            self.pargl     = list(copy_sig.pargl)
            self.kargl     = list(copy_sig.kargl)
            self.def_argv  = copy_sig.def_argv.copy()
            self.var_pargs = copy_sig.var_pargs
            self.var_kargs = copy_sig.var_kargs

        else:
            # Extract function signature, default arguments, keyword-only
            # arguments, and whether or not variable positional or keyword
            # arguments are allowed.  This also supports calling decorated
            # unbound instance, class, or static methods, though the only
            # time those would come into play would be if you called read
            # such a method directly from its owner's __dict__ (bypassing
            # the method object's own __get__ descriptor method).

            if isinstance(f, types.MethodType):
                # A bound instance or class method.
                argspec = getfullargspec(f.__func__)
                self.pargl = (argspec[0])[1:]
            elif isinstance(f, classmethod):
                # An unbound class method.
                if hasattr(f, '__func__'):
                    argspec = getfullargspec(f.__func__)
                else:
                    # No classmethod.__func__ in Python 2.6
                    argspec = getfullargspec(f.__get__(1).__func__)
                self.pargl = (argspec[0])[1:]
            elif isinstance(f, staticmethod):
                # An unbound static method.
                if hasattr(f, '__func__'):
                    argspec = getfullargspec(f.__func__)
                else:
                    # No staticmethod.__func__ in Python 2.6
                    argspec = getfullargspec(f.__get__(1))
                self.pargl = (argspec[0])[:]
            else:
                # A regular function, an unbound instance method, or a
                # bound static method.
                argspec = getfullargspec(f)
                self.pargl = (argspec[0])[:]

            if argspec[3] is not None:
                def_offset = len(self.pargl) - len(argspec[3])
                self.def_argv = dict((self.pargl[def_offset+i],argspec[3][i]) \
                                         for i in range(len(argspec[3])))
            else:
                self.def_argv = {}

            # For future support of Python 3 keyword-only arguments
            self.kargl = []

            self.var_pargs = argspec[1] is not None
            self.var_kargs = argspec[2] is not None

        if hasattr(f, '__doc__'):
            self.__doc__ = f.__doc__
        if hasattr(f, '__name__'):
            self.__name__ = f.__name__

    def __get__(self, inst, owner=None):
        return self.__class__(self.f.__get__(inst, owner))

    def __call__(self, *apply_pv, **apply_kv):
        new_argv = self.argv.copy()
        extra_argv = []

        for v in apply_pv:
            arg_i = None
            for name in self.pargl:
                if not name in new_argv:
                    arg_i = name
                    break

            if arg_i:
                new_argv[arg_i] = v
            else:
                extra_argv.append(v)

        for k,v in apply_kv.items():
            if not (self.var_kargs or (k in self.pargl) or (k in self.kargl)):
                raise TypeError("%s() got an unexpected keyword argument '%s'" % (self.__name__, k))
            new_argv[k] = v

        app_argv = self.def_argv.copy()
        app_argv.update(new_argv)

        app_ready = True
        for name in self.pargl:
            if not name in app_argv:
                app_ready = False
                break

        if app_ready:
            for name in self.kargl:
                if not name in app_argv:
                    app_ready = False
                    break

        if app_ready:
            fpargs = [new_argv[n] for n in self.pargl if n in new_argv] + extra_argv
            fkargs = dict((key,val) for key,val in new_argv.items() if not key in self.pargl)
            return self.f(*fpargs, **fkargs)
        else:
            return self.__class__(self.f, argv=new_argv, copy_sig=self)

class pointfree(partial):
    """@pointfree function decorator

    Converts a regular Python function into one which can be composed with
    other Python functions using the * and >> operators.  Functions with
    this decorator also automatically support partial application.

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
    print(output)
