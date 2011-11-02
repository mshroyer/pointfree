#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import partial, pointfree

### PARTIAL APPLICATION TESTS #############################################

@partial
def partial_adder(a, b, c):
    return a + 2*b + 3*c

@partial
def partial_adder_defaults(a, b, c=3):
    return a + 2*b + 3*c

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

class PartialFunctionCase(unittest.TestCase):
    def testNormalApplication(self):
        self.assertEqual(partial_adder(1,2,3), 14)
        self.assertEqual(partial_adder(a=1,b=2,c=3), 14)

    def testPartialApplication(self):
        self.assertEqual(partial_adder(1)(2)(3), 14)
        self.assertEqual(partial_adder(1,2)(3), 14)
        self.assertEqual(partial_adder(1)(2,3), 14)
        self.assertEqual(partial_adder()(1)()(2)()(3), 14)

    def testPartialKeywords(self):
        self.assertEqual(partial_adder(c=3)(1,2), 14)

class PartialFunctionDefaultsCase(unittest.TestCase):
    def testNormalApplication(self):
        self.assertEqual(partial_adder_defaults(1,2), 14)
        self.assertEqual(partial_adder_defaults(1,2,4), 17)

if __name__ == '__main__':
    unittest.main()
