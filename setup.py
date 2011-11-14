#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pointfree',
    version='1.0.0',
    description='Pointfree style toolkit for Python',
    long_description="""
pointfree is a small module that makes certain functional programming
constructs more convenient to use in Python.

Specifically, it provides:

* A decorator to enable *automatic* partial application of functions and
  methods.
* Notations for function composition through operator overloading.
* Helper functions to make composing generators more elegant.

The objective is to support the `pointfree programming style`_ in a
lightweight and easy to use manner -- and in particular, to serve as a nice
syntax for the kind of generator pipelines described in David Beazley's
PyCon 2008 presentation, `"Generator Tricks for Systems Programmers"`_.

.. _`pointfree programming style`: http://www.haskell.org/haskellwiki/Pointfree

.. _`"Generator Tricks for Systems Programmers"`: http://www.dabeaz.com/generators/Generators.pdf

Full documentation is available on the web at:

http://markshroyer.com/docs/pointfree/latest/
""",
    author='Mark Shroyer',
    author_email='code@markshroyer.com',
    url='https://github.com/markshroyer/pointfree',
    py_modules=['pointfree'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        ]
    )
