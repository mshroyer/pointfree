from pointfree import *
from test.pointfree_test import TestCase

### KEYWORD-ONLY FUNCTION FIXTURES ########################################

def kwonly_pure_func(a, b, *, c):
    return a + b + c

@partial
def kwonly_func(a, b, *, c):
    return a + b + c

@partial
def kwonly_defaults_func(a, b, *, c=3):
    return a + b + c

@partial
def kwonly_varkw_func(a, b, *, c, **kwargs):
    return (a + b + c, kwargs)

### KEYWORD-ONLY FUNCTION TESTS ###########################################

class KwOnlyArgsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(kwonly_func(1,2,c=3), 6)

    def testPartialApplication(self):
        self.assertEqual(kwonly_func(1)(2)(c=3), 6)
        self.assertEqual(kwonly_func(1,2)(c=3), 6)
        self.assertEqual(kwonly_func(1)(2,c=3), 6)
        self.assertEqual(kwonly_func(c=3)(1,2), 6)
        self.assertEqual(kwonly_func(c=3)(1)(2), 6)
        self.assertEqual(kwonly_func(a=1)(b=2)(c=3), 6)

    def testTooManyPositionalArguments(self):
        self.assertRaises(TypeError, lambda: kwonly_func(1,2,3))

    def testTooManyKeywordArguments(self):
        self.assertRaises(TypeError, lambda: kwonly_func(d=1))

class KwOnlyDefaultsCase(TestCase):
    def testNormalApplication(self):
        self.assertEqual(kwonly_defaults_func(1,2,c=4), 7)

    def testDefaultApplication(self):
        self.assertEqual(kwonly_defaults_func(1,2), 6)

class KwOnlyAndVarKargsCase(TestCase):
    def testNormalApplication(self):
        value, kwargs = kwonly_varkw_func(1,2,c=3,d=4,e=5)
        self.assertEqual(value, 6)
        self.assertDictEqual(kwargs, {'d': 4, 'e': 5})

### END TESTS #############################################################
