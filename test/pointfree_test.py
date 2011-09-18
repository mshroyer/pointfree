#!/usr/bin/env python

import os, sys, unittest, types
from pointfree import *

@curryable
def add(a, b):
    return a + b

@curryable
def mul(a, b):
    return a * b

class CurryableClass:
    def __init__(self, n):
        self.n = n

    @curryable
    def added_with(self, a, b):
        return self.n + a + b

class CurryingFunctionsTest(unittest.TestCase):
    """Function currying tests"""

    def testCurryingSimple(self):
        """Check that basic partial application works"""

        add1  = add(1)
        self.assertEqual(add1(3), 4)

        mul2 = mul(2)
        self.assertEqual(mul2(4), 8)

    def testCurryingSingleApplication(self):
        """Check single application of a curried function

        We must still be able to apply a curried function to all its
        arguments simultaneously.

        """

        self.assertEqual(add(1, 2), 3)
        self.assertEqual(mul(2, 3), 6)

    def testCurryingTooManyArgs(self):
        """Error handling: too many arguments

        An exception should be thrown if the curried function is applied to
        an argument list longer than it can accept.

        """

        with self.assertRaises(TypeError):
            add(1, 2, 3)

    def testCurryingNoArgs(self):
        """Edge case: zero arguments applied

        The curryable function should return a functionally (though not
        necessarily referentially identical) function if it is applied to
        an empty argument list one or more times.

        """

        f = add()
        self.assertEqual(f(1, 2), 3)

        g = mul()()()
        self.assertEqual(g(3, 4), 12)
        
class CurryingInstanceMethodsTest(unittest.TestCase):
    """Instance method currying tests"""

    def testCurryingInstanceMethods(self):
        obj = CurryableClass(1)
        f = obj.added_with(2)
        self.assertEqual(f(3), 6)
        
if __name__ == '__main__':
    unittest.main()
