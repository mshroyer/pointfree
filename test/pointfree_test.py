#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import partial, pointfree

### PARTIAL APPLICATION TESTS #############################################

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

class PartialThing(object):
    m = 1

    def __init__(self, n):
        self.n = n

    @partial
    def instance_adder(self, a, b, c):
        return self.n + a + 2*b + 3*c

    @partial
    @classmethod
    def class_adder(klass, a, b, c):
        return klass.m + a + 2*b + 3*c

    @partial
    @staticmethod
    def static_adder(a, b, c):
        return a + 2*b + 3*c

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

if __name__ == '__main__':
    unittest.main()
