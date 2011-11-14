#!/usr/bin/env python

# Runs all the unit tests and doctests for pointfree in one go.
#
# Note that the unit tests in test/pointfree_test.py are intended as the
# canonical indication of whether pointfree works on a given platform; the
# doctests fail in IronPython and CPython 3.0 for unimportant reasons, but
# the unittests pass on those platforms.
#
# Mark Shroyer
# Mon Nov 14 00:19:27 EST 2011

from __future__ import print_function

DOCTEST_FILENAMES = set(["overview.rst", "module.rst", "faq.rst"])

import sys, unittest, doctest, inspect
from os.path import realpath, join, dirname

project_path = realpath(join(dirname(__file__), '..'))

sys.path = [project_path] + sys.path
import pointfree, test.pointfree_test

class PFDocTestFinder(doctest.DocTestFinder):
    """A modified doctest.DocTestFinder which treats partial and
    pointfree instances as functions for the purpose of test
    gathering.

    Based on code from Python 3.2.2's doctest.py.
    
    """

    def _find(self, tests, obj, name, module, source_lines, globs, seen):
        """
        Find tests for the given object and any contained objects, and
        add them to `tests`.
        """
        if self._verbose:
            print('Finding tests in %s' % name)

        # If we've already processed this object, then ignore it.
        if id(obj) in seen:
            return
        seen[id(obj)] = 1

        # Find a test for this object, and add it to the list of tests.
        test = self._get_test(obj, name, module, globs, source_lines)
        if test is not None:
            tests.append(test)

        # Look for tests in a module's contained objects.
        if inspect.ismodule(obj) and self._recurse:
            for valname, val in obj.__dict__.items():
                valname = '%s.%s' % (name, valname)
                # Recurse to functions & classes.
                if ((inspect.isfunction(val) or inspect.isclass(val) or isinstance(val, pointfree.partial)) and
                    self._from_module(module, val)):
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)

        # Look for tests in a module's __test__ dictionary.
        if inspect.ismodule(obj) and self._recurse:
            for valname, val in getattr(obj, '__test__', {}).items():
                if not isinstance(valname, str):
                    raise ValueError("DocTestFinder.find: __test__ keys "
                                     "must be strings: %r" %
                                     (type(valname),))
                if not (inspect.isfunction(val) or inspect.isclass(val) or
                        inspect.ismethod(val) or inspect.ismodule(val) or
                        isinstance(val, str)):
                    raise ValueError("DocTestFinder.find: __test__ values "
                                     "must be strings, functions, methods, "
                                     "classes, or modules: %r" %
                                     (type(val),))
                valname = '%s.__test__.%s' % (name, valname)
                self._find(tests, val, valname, module, source_lines,
                           globs, seen)

        # Look for tests in a class's contained objects.
        if inspect.isclass(obj) and self._recurse:
            for valname, val in obj.__dict__.items():
                # Special handling for staticmethod/classmethod.
                if isinstance(val, staticmethod):
                    val = getattr(obj, valname)
                if isinstance(val, classmethod):
                    val = getattr(obj, valname).__func__

                # Recurse to methods, properties, and nested classes.
                if ((inspect.isfunction(val) or inspect.isclass(val) or
                      isinstance(val, property)) and
                      self._from_module(module, val)):
                    valname = '%s.%s' % (name, valname)
                    self._find(tests, val, valname, module, source_lines,
                               globs, seen)


if __name__ == '__main__':
    unittest_suite = unittest.TestSuite()
    unittest_suite.addTest(unittest.TestLoader().loadTestsFromModule(test.pointfree_test))

    def make_docfilesuite(filename):
        return doctest.DocFileSuite(join(project_path, "doc", filename), module_relative=False)

    doctest_suite = unittest.TestSuite()
    for filename in DOCTEST_FILENAMES:
        doctest_suite.addTest(make_docfilesuite(filename))
    doctest_suite.addTest(doctest.DocTestSuite(pointfree, test_finder=PFDocTestFinder()))

    test_runner = unittest.TextTestRunner(verbosity=1)

    print("""
######################################################################
#               Running unit tests in test/ directory                #
######################################################################""")
    test_runner.run(unittest_suite)

    print("""
######################################################################
#                          Running doctests                          #
######################################################################""")
    test_runner.run(doctest_suite)
