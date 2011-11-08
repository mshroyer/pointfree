#!/usr/bin/env python

from __future__ import print_function

import unittest, doctest
import pointfree, test.pointfree_test

if __name__ == '__main__':
    unittest_suite = unittest.TestSuite()
    unittest_suite.addTest(unittest.TestLoader().loadTestsFromModule(test.pointfree_test))

    doctest_suite = unittest.TestSuite()
    doctest_suite.addTest(doctest.DocFileSuite("README.rst"))
    doctest_suite.addTest(doctest.DocTestSuite(pointfree))

    test_runner = unittest.TextTestRunner(verbosity=1)

    print("Running unit tests from test.pointfree_test:")
    test_runner.run(unittest_suite)

    print("\nRunning doctests:")
    test_runner.run(doctest_suite)
