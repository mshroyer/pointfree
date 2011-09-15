#!/usr/bin/env python

from distutils.core import setup

setup(name='fpkit',
      version='0.1',
      description='Functional programming toolkit for Python',
      author='Mark Shroyer',
      author_email='code@markshroyer.com',
      url='https://github.com/markshroyer/python-fpkit',
      py_modules=['fpkit'],
      package_dir = {'': 'src'}
      )
