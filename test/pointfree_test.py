#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import composable, currying

### COMPOSABLE TESTING ####################################################

@composable
def composable_add(a):
    return 5 + a

@composable
def composable_mul(a):
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
        f = composable_add * composable_mul
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

### CURRYING TESTING ######################################################

@currying
def currying_add(a, b, c):
    return a + b + c

@currying
def currying_mul(a, b, c):
    return a * b * c

class CurryingThing(object):
    """Class test fixture for @currying decorator"""

    m = 3

    def __init__(self, n):
        self.n = n

    @currying
    def instance_add(self, a, b, c):
        return self.n + a + b + c

    @currying
    def instance_mul(self, a, b, c):
        return self.n * a * b * c

    # @currying
    # @classmethod
    # def class_add(klass, a, b, c):
    #     return klass.m + a + b + c

    # @currying
    # @classmethod
    # def class_mul(klass, a, b, c):
    #     return klass.m * a * b * c

    # @currying
    # @staticmethod
    # def static_add(a, b, c):
    #     return a + b + c

    # @currying
    # @staticmethod
    # def static_mul(a, b, c):
    #     return a * b * c
        
# class CurryingFunctionCase(unittest.TestCase):
#     def testFunctions(self):
#         f = currying_add(1, 2) * currying_mul(3, 4)
#         self.assertEqual(f(2), 27)

# class CurryingInstanceCase(unittest.TestCase):
#     def setUp(self):
#         self.t = CurryingThing(2)

#     def testInstanceMethods(self):
#         f = self.t.instance_add(1, 2) * self.t.instance_mul(3, 4)
#         self.assertEqual(f(2), 53)

#     def testClassMethods(self):
#         f = self.t.class_add(1, 2) * self.t.class_mul(3, 4)
#         self.assertEqual(f(2), 78)

#     def testStaticMethods(self):
#         f = self.t.static_add(1, 2) * self.t.static_mul(3, 4)
#         self.assertEqual(f(2), 27)

if __name__ == '__main__':
    unittest.main()
