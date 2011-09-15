#!/usr/bin/env python

from distutils.core import setup

setup(name='pointfree',
      version='0.1',
      description='Functional programming toolkit for Python',
      author='Mark Shroyer',
      author_email='code@markshroyer.com',
      url='https://github.com/markshroyer/python-pointfree',
      py_modules=['pointfree'],
      package_dir = {'': 'src'}
      )
