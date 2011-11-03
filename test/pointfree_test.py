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

    def testVarArgsApplication(self):
        self.assertEqual(padd_var_args(1,2,3,4), 26)

if __name__ == '__main__':
    unittest.main()
