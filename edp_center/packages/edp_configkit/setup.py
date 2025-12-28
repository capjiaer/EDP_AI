#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

# 读取版本号
with open(os.path.join('__init__.py'), 'r', encoding='utf-8') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

# 读取长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='configkit',
    version=version,
    description='A library for configuration transformation between Python and Tcl',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Anping Chen',
    author_email='capjiaer@163.com',
    url='https://github.com/capjiaer/configkit',
    packages=find_packages(),
    install_requires=[
        'pyyaml>=5.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    keywords='configuration, tcl, yaml, conversion',
)
