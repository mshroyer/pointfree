from __future__ import print_function

__author__  = "Mark Shroyer"
__email__   = "code@markshroyer.com"
__version__ = 0.1

import inspect, types

class partial(object):
    """@partial function decorator

    Converts a regular Python function into one supporting a form of
    partial application.  Supports positional arguments only.

    """

    def __init__(self, f, argv={}, copy_sig=None):
        self.f = f
        self.argv = argv.copy()

        if copy_sig is not None:
            self.pargl     = list(copy_sig.pargl)
            self.kargl     = copy_sig.kargl.copy()
            self.def_argv  = copy_sig.def_argv.copy()
            self.var_pargs = copy_sig.var_pargs
            self.var_kargs = copy_sig.var_kargs
        elif not (isinstance(f, classmethod) or isinstance(f, staticmethod)):
            if isinstance(f, types.MethodType):
                argspec = inspect.getargspec(f.__func__)
                self.pargl = (argspec[0])[1:]
            else:
                argspec = inspect.getargspec(f)
                self.pargl = (argspec[0])[:]

            if argspec[3] is not None:
                def_offset = len(self.pargl) - len(argspec[3])
                self.def_argv = dict((self.pargl[def_offset+i],argspec[3][i]) \
                                         for i in xrange(len(argspec[3])))
            else:
                self.def_argv = {}

            # For future support of Python 3 keyword-only arguments
            self.kargl = {}

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
                if not new_argv.has_key(name):
                    arg_i = name
                    break

            if arg_i:
                new_argv[arg_i] = v
            else:
                extra_argv.append(v)

        for k,v in apply_kv.iteritems():
            if not (self.var_kargs or (k in self.pargl) or (k in self.kargl.keys())):
                raise TypeError("%s() got an unexpected keyword argument '%s'" % (self.__name__, k))
            new_argv[k] = v

        app_argv = self.def_argv.copy()
        app_argv.update(new_argv)

        app_ready = True
        for name in self.pargl:
            if not app_argv.has_key(name):
                app_ready = False
                break

        if app_ready:
            for name in self.kargl.keys():
                if not app_argv.has_key(name):
                    app_ready = False
                    break

        if app_ready:
            fpargs = [new_argv[n] for n in self.pargl if new_argv.has_key(n)] + extra_argv
            fkargs = dict((key,val) for key,val in new_argv.iteritems() if not key in self.pargl)
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
