#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pointfree',
      version='0.1',
      description='Functional programming toolkit for Python',
      long_description=read('README.md'),
      license="BSD",
      author='Mark Shroyer',
      author_email='code@markshroyer.com',
      url='https://github.com/markshroyer/python-pointfree',
      py_modules=['pointfree'],
      test_suite='test'
      )
