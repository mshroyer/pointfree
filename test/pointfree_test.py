#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import partial, pointfree

### CURRYING TESTING ######################################################

@pointfree
def currying_add(a, b, c):
    return a + b + c

@pointfree
def currying_mul(a, b, c):
    return a * b * c

class CurryingThing(object):
    """Class test fixture for @pointfree decorator"""

    m = 3

    def __init__(self, n):
        self.n = n

    @pointfree
    def instance_add(self, a, b, c):
        return self.n + a + b + c

    @pointfree
    def instance_mul(self, a, b, c):
        return self.n * a * b * c

    @pointfree
    @classmethod
    def class_add(klass, a, b, c):
        return klass.m + a + b + c

    @pointfree
    @classmethod
    def class_mul(klass, a, b, c):
        return klass.m * a * b * c

    @pointfree
    @staticmethod
    def static_add(a, b, c):
        return a + b + c

    @pointfree
    @staticmethod
    def static_mul(a, b, c):
        return a * b * c
        
class SimpleCurryingFunctionCase(unittest.TestCase):
    def testFunctions(self):
        f = currying_add(1, 2)
        self.assertEqual(f(3), 6)

class CurryingFunctionCase(unittest.TestCase):
    def testFunctions(self):
        f = currying_add(1, 2) * currying_mul(3, 4)
        self.assertEqual(f(2), 27)

class CurryingInstanceCase(unittest.TestCase):
    def setUp(self):
        self.t = CurryingThing(2)

    def testInstanceMethods(self):
        f = self.t.instance_add(1, 2) * self.t.instance_mul(3, 4)
        self.assertEqual(f(2), 53)

    def testClassMethods(self):
        f = self.t.class_add(1, 2) * self.t.class_mul(3, 4)
        self.assertEqual(f(2), 78)

    def testStaticMethods(self):
        f = self.t.static_add(1, 2) * self.t.static_mul(3, 4)
        self.assertEqual(f(2), 27)

class CurryingClassCase(unittest.TestCase):
    def testClassMethods(self):
        f = CurryingThing.class_add(1, 2) * CurryingThing.class_mul(3, 4)
        self.assertEqual(f(2), 78)

    def testStaticMethods(self):
        f = CurryingThing.static_add(1, 2) * CurryingThing.static_mul(3, 4)
        self.assertEqual(f(2), 27)

if __name__ == '__main__':
    unittest.main()
