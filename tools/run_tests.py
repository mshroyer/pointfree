#!/usr/bin/env python

from __future__ import print_function

import sys, unittest, doctest
from os.path import realpath, join, dirname

if __name__ == '__main__':
    project_path = realpath(join(dirname(__file__), '..'))

    sys.path = [project_path] + sys.path
    import pointfree, test.pointfree_test

    unittest_suite = unittest.TestSuite()
    unittest_suite.addTest(unittest.TestLoader().loadTestsFromModule(test.pointfree_test))

    def make_docfilesuite(filename):
        return doctest.DocFileSuite(join(project_path, "doc", filename), module_relative=False)

    doctest_suite = unittest.TestSuite()
    doctest_suite.addTest(make_docfilesuite("overview.rst"))
    doctest_suite.addTest(make_docfilesuite("faq.rst"))
    doctest_suite.addTest(doctest.DocTestSuite(pointfree))

    test_runner = unittest.TextTestRunner(verbosity=1)

    print("Running unit tests from test.pointfree_test:")
    test_runner.run(unittest_suite)

    print("\nRunning doctests:")
    test_runner.run(doctest_suite)
