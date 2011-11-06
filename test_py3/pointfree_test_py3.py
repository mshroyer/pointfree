from unittest import TestCase
from pointfree import *

def kwonly_pure_func(a, b, *, c):
    return a + b + c

@partial
def kwonly_func(a, b, *, c):
    return a + b + c

class KwOnlyArgsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(kwonly_func(1,2,c=3), 6)

    def testPartialApplication(self):
        self.assertEqual(kwonly_func(1)(2)(c=3), 6)
        self.assertEqual(kwonly_func(1,2)(c=3), 6)
        self.assertEqual(kwonly_func(1)(2,c=3), 6)
        self.assertEqual(kwonly_func(c=3)(1,2), 6)
        self.assertEqual(kwonly_func(c=3)(1)(2), 6)

    def testKeywordOnlyApplication(self):
        self.assertRaises(TypeError, lambda *a: kwonly_func(1,2,3))
