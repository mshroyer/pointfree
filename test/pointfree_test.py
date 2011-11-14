import os, sys, unittest, types, functools, operator
from pointfree import *

# The unittest.TestCase in Python 2.6 and 3.0 doesn't have some of the
# methods that we use in our test suite, so...
if hasattr(unittest.TestCase, 'assertIsInstance') \
        and hasattr(unittest.TestCase, 'assertDictEqual') \
        and hasattr(unittest.TestCase, 'assertIsNone'):
    from unittest import TestCase
else:
    class TestCase(unittest.TestCase):
        def assertIsInstance(self, f, klass):
            self.assertTrue(isinstance(f, klass))

        def assertDictEqual(self, a, b):
            self.assertTrue(a == b)

        def assertIsNone(self, x):
            self.assertTrue(x is None)

### PARTIAL APPLICATION FIXTURES ##########################################

@partial
def padd(a, b, c):
    return a + 2*b + 3*c

@partial
def padd_defaults(a, b, c=3):
    return a + 2*b + 3*c

@partial
def padd_var_args(a, b, *args):
    return a + 2*b + 3*sum(args)

@partial
def padd_var_kargs(a, b, **kargs):
    return (a + 2*b, kargs)

@partial
def padd_var_args_kargs(a, b, *args, **kargs):
    return (a + 2*b + 3*sum(args), kargs)

@partial
def padd_var_args_defaults(a, b, c=3, *args):
    return a + 2*b + 3*c + 4*sum(args)

class PartialThing(object):
    m = 1

    def __init__(self, n):
        self.n = n

    @partial
    def instance_padd(self, a, b, c):
        return self.n + a + 2*b + 3*c

    @partial
    @classmethod
    def class_padd(klass, a, b, c):
        return klass.m + a + 2*b + 3*c

    @partial
    @staticmethod
    def static_padd(a, b, c):
        return a + 2*b + 3*c

    @classmethod
    @partial
    def class_padd_in(klass, a, b, c):
        return klass.m + a + 2*b + 3*c

    @staticmethod
    @partial
    def static_padd_in(a, b, c):
        return a + 2*b + 3*c

### PARTIAL APPLICATION TESTS #############################################

class PartialFuncCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd(1,2,3), 14)

    def testNormalKeywordApplication(self):
        self.assertEqual(padd(a=1,b=2,c=3), 14)

    def testPartialApplication(self):
        self.assertEqual(padd(1)(2)(3), 14)

    def testClusteredPartialApplication(self):
        self.assertEqual(padd(1,2)(3), 14)
        self.assertEqual(padd(1)(2,3), 14)

    def testInterspersedPartialApplication(self):
        self.assertEqual(padd()(1)()(2)()(3), 14)

    def testPartialKeywords(self):
        self.assertEqual(padd(c=3)(1,2), 14)

    def testPartialKeywordsOutOfOrder(self):
        self.assertEqual(padd(b=2)(a=1)(3), 14)
        self.assertEqual(padd(b=2)(c=3)(a=1), 14)

class PartialFuncDefaultsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_defaults(1,2), 14)

    def testPositionalOverride(self):
        self.assertEqual(padd_defaults(1,2,4), 17)

    def testKeywordOverride(self):
        self.assertEqual(padd_defaults(c=4)(1,2), 17)

class PartialFuncConcurrencyCase(TestCase):
    def testReusedPartialApplication(self):
        p = padd(1)
        self.assertEqual(p(2,3), 14)

        # Fully applying p the first time shouldn't change its state; we
        # must be able to reuse it.
        self.assertIsInstance(p(), partial)
        self.assertEqual(p(2)(3), 14)

class PartialFuncErrorCase(TestCase):
    def testTooManyArgsError(self):
        self.assertRaises(TypeError, lambda: padd(1,2,3,4))

    def testPartialTooManyArgsError(self):
        self.assertRaises(TypeError, lambda: padd(1)(2)(3,4))

    def testTooManyKargsError(self):
        self.assertRaises(TypeError, lambda: padd(1,2,3,d=4))

    def testTooManyKargsEarlyError(self):
        """Make sure we raise an error as soon as we can possibly determine
        we've passed an invalid keyword argument to the function."""

        self.assertRaises(TypeError, lambda: padd(d=4))

    def testNoMultipleArgValsError(self):
        """Even though this wouldn't be legal with a regular Python
        function, I think it's convenient to allow arguments to be multiply
        specified in partial functions."""
        
        self.assertEqual(padd(1,2,3,a=4,b=5,c=6), 32)
        self.assertEqual(padd(1,2)(a=3)(4), 19)

class PartialFuncVarArgsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_var_args(1,2), 5)

    def testPartialApplication(self):
        self.assertEqual(padd_var_args(1)(2), 5)

    def testVarArgsApplication(self):
        self.assertEqual(padd_var_args(1,2,3,4), 26)

    def testVarArgsPartialApplication(self):
        self.assertEqual(padd_var_args(1)(2,3,4,5), 41)

class PartialFuncVarKargsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_var_kargs(1,2)[0], 5)

    def testNormalKeywordsApplication(self):
        self.assertEqual(padd_var_kargs(a=1,b=2)[0], 5)

    def testPartialApplication(self):
        self.assertEqual(padd_var_kargs(1)(2)[0], 5)

    def testVarKargsApplication(self):
        val,kargs = padd_var_kargs(1,2,c=3)
        self.assertEqual(val, 5)
        self.assertDictEqual(kargs, {'c': 3})

    def testVarKargsPartialApplication(self):
        val,kargs = padd_var_kargs(a=1)(c=3,d=4)(2)
        self.assertEqual(val, 5)
        self.assertDictEqual(kargs, {'c': 3, 'd': 4})

class PartialFuncVarArgsKargsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_var_args_kargs(1,2)[0], 5)

    def testVarArgsKargsApplication(self):
        val,kargs = padd_var_args_kargs(1,2,3,4,c=5,d=6)
        self.assertEqual(val, 26)
        self.assertDictEqual(kargs, {'c': 5, 'd': 6})

    def testVarArgKargsPartialApplication(self):
        val,kargs = padd_var_args_kargs(1,c=5)(d=6)(2,3,4)
        self.assertEqual(val, 26)
        self.assertDictEqual(kargs, {'c': 5, 'd': 6})

class PartialFuncVarArgsDefaultsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_var_args_defaults(1,2), 14)
        self.assertEqual(padd_var_args_defaults(1,2,4), 17)
        self.assertEqual(padd_var_args_defaults(1,2,4,5), 37)

    def testPartialApplication(self):
        self.assertEqual(padd_var_args_defaults(1)(2), 14)
        self.assertEqual(padd_var_args_defaults(1)(2,4), 17)
        self.assertEqual(padd_var_args_defaults(1)(2,4,5), 37)

    def testPartialKwargApplication(self):
        self.assertEqual(padd_var_args_defaults(b=2)(1,4,5), 37)

class PartialMethodCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.instance_padd(1,2,3), 16)

    def testPartialApplication(self):
        self.assertEqual(self.inst.instance_padd(1)(2)(3), 16)

class PartialClassMethodCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.class_padd(1,2,3), 15)
        self.assertEqual(PartialThing.class_padd(1,2,3), 15)

    def testPartialApplication(self):
        self.assertEqual(self.inst.class_padd(1)(2)(3), 15)
        self.assertEqual(PartialThing.class_padd(1)(2)(3), 15)

class PartialStaticMethodCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.static_padd(1,2,3), 14)
        self.assertEqual(PartialThing.static_padd(1,2,3), 14)

    def testPartialApplication(self):
        self.assertEqual(self.inst.static_padd(1)(2)(3), 14)
        self.assertEqual(PartialThing.static_padd(1)(2)(3), 14)

class PartialClassMethodInnerCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testClassMethodType(self):
        self.assertIsInstance(self.inst.class_padd_in, types.MethodType)
        self.assertIsInstance(PartialThing.class_padd_in, types.MethodType)

    def testNormalApplication(self):
        self.assertEqual(self.inst.class_padd_in(1,2,3), 15)
        self.assertEqual(PartialThing.class_padd_in(1,2,3), 15)

    def testPartialApplication(self):
        self.assertEqual(self.inst.class_padd_in(1)(2)(3), 15)
        self.assertEqual(PartialThing.class_padd_in(1)(2)(3), 15)

class PartialStaticMethodInnerCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.static_padd_in(1,2,3), 14)
        self.assertEqual(PartialThing.static_padd_in(1,2,3), 14)

    def testPartialApplication(self):
        self.assertEqual(self.inst.static_padd_in(1)(2)(3), 14)
        self.assertEqual(PartialThing.static_padd_in(1)(2)(3), 14)

class PartialUnboundMethodsCase(TestCase):
    def setUp(self):
        self.inst = PartialThing(2)
        self.instance_padd = PartialThing.__dict__['instance_padd']

    def testInstanceMethodNormalApplication(self):
        self.assertEqual(self.instance_padd(self.inst,1,2,3), 16)

    def testInstanceMethodPartialApplication(self):
        self.assertEqual(self.instance_padd(self.inst)(1,2)(3), 16)

### __INIT__ ARGUMENT FIXTURES ############################################

def just_add(a, b, c):
    return a + b + c

def just_add2(a, b, *args):
    return a + b + sum(args)

### __INIT__ ARGUMENT TESTS ###############################################

class ArgsToInitCase(TestCase):
    def testArgumentsToInit(self):
        self.assertEqual(partial(just_add)(1, 2, 3), 6)
        self.assertEqual(partial(just_add, 1, 2)(3), 6)
        self.assertEqual(partial(just_add, 1)(2)(3), 6)

    def testFullArguments(self):
        p = partial(just_add, 1, 2, 3)

        # partial(just_add, 1, 2, 3) should still be a partial instance,
        # even though we've specified enough arguments that the function
        # can be fully applied.
        self.assertIsInstance(p, partial)

        # And when we call this object with no arguments, the function
        # should be evaluated.
        self.assertEqual(p(), 6)

class ExtraArgsToInitCase(TestCase):
    """Make sure partial behaves as expected when extra arguments are
    provided to the __init__ method."""

    def testExtraArgsToInit(self):
        p = partial(just_add2, 1, 2, 3, 4, 5)
        self.assertIsInstance(p, partial)
        self.assertEqual(p(), 15)
        self.assertEqual(p(6, 7), 28)

    def testTooManyArgsToInit(self):
        self.assertRaises(TypeError, lambda: partial(just_add, 1, 2, 3, 4))
        self.assertRaises(TypeError, lambda: partial(just_add, d=4))

class FunctoolsPartialCase(TestCase):
    """Make sure pointfree.partial can accept a functools.partial as an
    argument (though this won't work if the functools.partial instance
    wraps a builtin Python function."""

    def testFunctoolsPartialInit(self):
        self.assertEqual(partial(functools.partial(just_add))(1, 2, 3), 6)
        self.assertEqual(partial(functools.partial(just_add, 1, 2))(3), 6)
        self.assertEqual(partial(functools.partial(just_add, 1, 2, 3))(), 6)

    def testEarlyError(self):
        self.assertRaises(TypeError, lambda: partial(functools.partial(just_add, 1, 2, 3, 4)))

class PointfreePartialCase(TestCase):
    """Make sure partial can accept one of its own instances as an
    argument."""

    def testPartialPartial(self):
        self.assertEqual(partial(partial(just_add))(1, 2, 3), 6)
        self.assertEqual(partial(partial(just_add, 1, 2), 3)(), 6)
        self.assertEqual(partial(partial(just_add), 1)(2)(3), 6)
        self.assertEqual(partial(partial(just_add, 1)(2))(3), 6)

### POINTFREE OPERATOR FIXTURES ###########################################

@pointfree
def cadd(a, b):
    return a + b

@pointfree
def cmul(a, b):
    return a * b

class PointfreeThing(object):
    m = 1

    def __init__(self, n):
        self.n = n

    @pointfree
    def instance_cadd(self, a, b, c):
        return self.n + a + 2*b + 3*c

    @pointfree
    @classmethod
    def class_cadd(klass, a, b, c):
        return klass.m + a + 2*b + 3*c

    @pointfree
    @staticmethod
    def static_cadd(a, b, c):
        return a + 2*b + 3*c

    @classmethod
    @pointfree
    def class_cadd_in(klass, a, b, c):
        return klass.m + a + 2*b + 3*c

    @staticmethod
    @pointfree
    def static_cadd_in(a, b, c):
        return a + 2*b + 3*c

### POINTFREE OPERATOR TESTS ##############################################

class PointfreeFuncCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(cadd(2,3), 5)
        self.assertEqual(cmul(2,3), 6)

    def testPartialApplication(self):
        self.assertIsInstance(cadd(2), pointfree)
        self.assertEqual(cadd(2)(3), 5)

    def testCompOperator(self):
        f = cadd(3) * cmul(2)
        self.assertEqual(f(5), 13)

    def testCompOperatorMultiple(self):
        f = cadd(3) * cmul(2) * cadd(1)
        self.assertEqual(f(1), 7)

    def testForwardOperator(self):
        f = cmul(2) >> cadd(3)
        self.assertEqual(f(5), 13)

class PointfreeFuncMultipleArgCase(TestCase):
    def setUp(self):
        self.f = cadd(1) * cmul

    def testNormalApplication(self):
        self.assertEqual(self.f(3,4), 13)

    def testPartialApplication(self):
        self.assertEqual(self.f(3)(4), 13)

class PointfreeChainedOperatorsCase(TestCase):
    def testMultipleCompOperators(self):
        f = cadd(2) * cmul(3) * cadd(4)
        self.assertEqual(f(1), 17)

    def testMultipleForwardOperators(self):
        f = cadd(2) \
            >> cmul(3) \
            >> cadd(4)
        self.assertEqual(f(1), 13)

class PointfreeMethodCase(TestCase):
    def setUp(self):
        self.i = PointfreeThing(2)

    def testNormalApplication(self):
        f = self.i.instance_cadd(1,2) * self.i.instance_cadd(3,4)
        self.assertEqual(f(1), 55)

    def testPartialApplication(self):
        f = self.i.instance_cadd(1,2) * self.i.instance_cadd
        self.assertEqual(f(3,4,1), 55)
        self.assertEqual(f(3)(4)(1), 55)
        self.assertEqual(f(c=1)(3)(4), 55)

class PointfreeClassMethodCase(TestCase):
    def setUp(self):
        self.i = PointfreeThing(2)

    def testNormalApplicationFromInstance(self):
        f = self.i.class_cadd(1,2) * self.i.class_cadd(3,4)
        self.assertEqual(f(1), 51)

    def testNormalApplicationFromClass(self):
        g = PointfreeThing.class_cadd(1,2) * PointfreeThing.class_cadd(3,4)
        self.assertEqual(g(1), 51)

    def testPartialApplicationFromInstance(self):
        f = self.i.class_cadd(1,2) * self.i.class_cadd
        self.assertEqual(f(1,2,3), 51)
        self.assertEqual(f(1)(2)(3), 51)
        self.assertEqual(f(c=3)(1)(2), 51)

    def testPartialApplicationFromClass(self):
        f = PointfreeThing.class_cadd(1,2) * PointfreeThing.class_cadd
        self.assertEqual(f(1,2,3), 51)
        self.assertEqual(f(1)(2)(3), 51)
        self.assertEqual(f(c=3)(1)(2), 51)

class PointfreeStaticMethodCase(TestCase):
    def setUp(self):
        self.i = PointfreeThing(2)

    def testNormalApplicationFromInstance(self):
        f = self.i.static_cadd(1,2) * self.i.static_cadd(3,4)
        self.assertEqual(f(1), 47)

    def testNormalApplicationFromClass(self):
        f = PointfreeThing.static_cadd(1,2) * PointfreeThing.static_cadd(3,4)
        self.assertEqual(f(1), 47)

    def testPartialApplicationFromInstance(self):
        f = self.i.static_cadd(1,2) * self.i.static_cadd
        self.assertEqual(f(1,2,3), 47)
        self.assertEqual(f(1)(2)(3), 47)
        self.assertEqual(f(c=3)(1)(2), 47)

    def testPartialApplicationFromClass(self):
        f = PointfreeThing.static_cadd(1,2) * PointfreeThing.static_cadd
        self.assertEqual(f(1,2,3), 47)
        self.assertEqual(f(1)(2)(3), 47)
        self.assertEqual(f(c=3)(1)(2), 47)

### HELPER FUNCTION TESTS #################################################

class HelperPfmapCase(TestCase):
    def testPfmap(self):
        fn = pfmap(lambda x: x+1)
        self.assertEqual(list(fn(range(5))), [1, 2, 3, 4, 5])

class HelperPfreduceCase(TestCase):
    def testPfreduce(self):
        fn = pfmap(lambda x: x+1) >> pfreduce(operator.add, initial=0)
        self.assertEqual(fn(range(5)), 15)

    def testPfreduceInitial(self):
        fn = pfreduce(operator.add, initial=2)
        self.assertEqual(fn([]), 2)
        self.assertEqual(fn([1,2]), 5)

    def testPfreduceNoInitial(self):
        fn = pfreduce(operator.add)
        self.assertIsNone(fn([]))

class HelperPfcollectCase(TestCase):
    def testPfcollect(self):
        fn = pf(lambda: range(5)) >> pfcollect
        self.assertEqual(fn(), [0, 1, 2, 3, 4])

class HelperPfignoreCase(TestCase):
    def testPfignore(self):
        result = []

        @pointfree
        def fn(iterator):
            for item in iterator:
                result.append(item)
                yield item

        (fn >> pfignore_all)(range(3))
        self.assertEqual(result, [0, 1, 2])
        

### PYTHON 3 KEYWORD-ONLY ARGS TESTS ######################################

# We can't lump the Python 3 keyword-only argument tests in here with the
# rest, because Python 2 doesn't recognize the keyword-only syntax and will
# fail to compile the module.  Instead we define these tests in a separate
# module and conditionally import them here...

if sys.version_info >= (3,0):
    from test.pointfree_py3 import *

### END TESTS #############################################################

if __name__ == '__main__':
    unittest.main()
