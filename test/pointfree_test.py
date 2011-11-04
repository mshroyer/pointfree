#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import partial, pointfree

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

class PartialFuncCase(unittest.TestCase):
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
        self.assertEqual(padd(b=2)(1)(3), 14)
        self.assertEqual(padd(b=2)(1,3), 14)

class PartialFuncDefaultsCase(unittest.TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_defaults(1,2), 14)

    def testPositionalOverride(self):
        self.assertEqual(padd_defaults(1,2,4), 17)

    def testKeywordOverride(self):
        self.assertEqual(padd_defaults(c=4)(1,2), 17)

class PartialFuncConcurrencyCase(unittest.TestCase):
    def testReusedPartialApplication(self):
        p = padd(1)
        self.assertEqual(p(2,3), 14)

        # Fully applying p the first time shouldn't change its state; we
        # must be able to reuse it.
        self.assertEqual(p(2)(3), 14)

class PartialFuncErrorCase(unittest.TestCase):
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

class PartialFuncVarArgsCase(unittest.TestCase):
    def testNormalApplication(self):
        self.assertEqual(padd_var_args(1,2), 5)

    def testPartialApplication(self):
        self.assertEqual(padd_var_args(1)(2), 5)

    def testVarArgsApplication(self):
        self.assertEqual(padd_var_args(1,2,3,4), 26)

    def testVarArgsPartialApplication(self):
        self.assertEqual(padd_var_args(1)(2,3,4,5), 41)

class PartialFuncVarKargsCase(unittest.TestCase):
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

class PartialFuncVarArgsKargsCase(unittest.TestCase):
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

class PartialFuncVarArgsDefaultsCase(unittest.TestCase):
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

class PartialMethodCase(unittest.TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.instance_padd(1,2,3), 16)

    def testPartialApplication(self):
        self.assertEqual(self.inst.instance_padd(1)(2)(3), 16)

class PartialClassMethodCase(unittest.TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.class_padd(1,2,3), 15)
        self.assertEqual(PartialThing.class_padd(1,2,3), 15)

    def testPartialApplication(self):
        self.assertEqual(self.inst.class_padd(1)(2)(3), 15)
        self.assertEqual(PartialThing.class_padd(1)(2)(3), 15)

class PartialStaticMethodCase(unittest.TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.static_padd(1,2,3), 14)
        self.assertEqual(PartialThing.static_padd(1,2,3), 14)

    def testPartialApplication(self):
        self.assertEqual(self.inst.static_padd(1)(2)(3), 14)
        self.assertEqual(PartialThing.static_padd(1)(2)(3), 14)

class PartialClassMethodInnerCase(unittest.TestCase):
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

class PartialStaticMethodInnerCase(unittest.TestCase):
    def setUp(self):
        self.inst = PartialThing(2)

    def testNormalApplication(self):
        self.assertEqual(self.inst.static_padd_in(1,2,3), 14)
        self.assertEqual(PartialThing.static_padd_in(1,2,3), 14)

    def testPartialApplication(self):
        self.assertEqual(self.inst.static_padd_in(1)(2)(3), 14)
        self.assertEqual(PartialThing.static_padd_in(1)(2)(3), 14)

### POINTFREE OPERATOR FIXTURES ###########################################

@pointfree
def cadd(a, b):
    return a + b

@pointfree
def cmul(a, b):
    return a * b

### POINTFREE OPERATOR TESTS ##############################################

class PointfreeFuncCase(unittest.TestCase):
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

class PointfreeFuncMultipleArgCase(unittest.TestCase):
    def setUp(self):
        self.f = cadd(1) * cmul

    def testNormalApplication(self):
        self.assertEqual(self.f(3,4), 13)

    def testPartialApplication(self):
        self.assertEqual(self.f(3)(4), 13)

### END TESTS #############################################################

if __name__ == '__main__':
    unittest.main()
