#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import *

@composable
def fun_add(a):
    return 5 + a

@composable
def fun_mul(a):
    return 5 * a

class ComposableThing(object):
    """Class test fixture for @composable decorator"""

    m = 3

    def __init__(self, n):
        self.n = n

    @composable
    def instance_add(self, a):
        return self.n + a

    @composable
    def instance_mul(self, a):
        return self.n * a

    @composable
    @classmethod
    def class_add(klass, a):
        return klass.m + a

    @composable
    @classmethod
    def class_mul(klass, a):
        return klass.m * a

    @composable
    @staticmethod
    def static_add(a):
        return 4 + a

    @composable
    @staticmethod
    def static_mul(a):
        return 4 * a
        
class ComposableFunctionCase(unittest.TestCase):
    """Function test cases for @composable"""

    def testFunctions(self):
        f = fun_add * fun_mul
        self.assertEqual(f(2), 15)

class ComposableInstanceCase(unittest.TestCase):
    """Instance test cases for @composable

    Tests that the @composable decorator works correctly when applied to
    methods which are subsequently accessed through an instance of their
    class.

    """

    def setUp(self):
        self.t = ComposableThing(2)

    def testInstanceMethods(self):
        f = self.t.instance_add * self.t.instance_mul
        self.assertEqual(f(2), 6)

    def testClassMethods(self):
        f = self.t.class_add * self.t.class_mul
        self.assertEqual(f(2), 9)

    def testStaticMethods(self):
        f = self.t.static_add * self.t.static_mul
        self.assertEqual(f(2), 12)

class ComposableClassCase(unittest.TestCase):
    """Class test cases for @composable

    Tests that the @composable decorator works correctly when applied to
    methods which are subsequently accessed directly through their class.

    """
    
    def testClassMethods(self):
        f = ComposableThing.class_add * ComposableThing.class_mul
        self.assertEqual(f(2), 9)

    def testStaticMethods(self):
        f = ComposableThing.static_add * ComposableThing.static_mul
        self.assertEqual(f(2), 12)

if __name__ == '__main__':
    unittest.main()
