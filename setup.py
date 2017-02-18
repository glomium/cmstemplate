#!/usr/bin/python
# ex:set fileencoding=utf-8:

from setuptools import setup
from setuptools import find_packages
import os

CLASSIFIERS = []

VERSION = ("0","9", "0")
NAME = os.path.basename(os.path.abspath(os.path.dirname(__file__)))

__version__ = '.'.join(VERSION)
__docformat__ = 'restructuredtext'

setup(
    name=NAME,
    version=__version__,
    packages=[],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
