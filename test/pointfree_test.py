import os, sys, unittest
from pointfree import *

class CurryingTest(unittest.TestCase):
    def testCurrying1(self):
        @curryable
        def add(a, b):
            return a + b

        @curryable
        def mult(a, b):
            return a * b

        add1  = add(1)
        mult2 = mult(2)

        self.assertEqual(add1(3), 4)
        self.assertEqual(mult2(4), 8)
