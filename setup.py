#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='pointfree',
    version='0.1',
    description='Pointfree style toolkit for Python',
    author='Mark Shroyer',
    author_email='code@markshroyer.com',
    url='https://github.com/markshroyer/python-pointfree',
    py_modules=['pointfree']
    )
