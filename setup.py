#!/usr/bin/env python

import os

from codecs import open
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open('requirements/base.txt') as f:
    install_requires = f.read().strip().split('\n')

with open('requirements/dev.txt') as f:
    dev_requires = f.read().strip().split('\n')

with open('VERSION', 'r') as f:
    version = f.read().rstrip()

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='skconfig',
    version=version,
    description='Scikit-learn sampling and validation library',
    long_description=readme,
    author='Thomas J Fan',
    author_email='thomasjpfan@gmail.com',
    url='https://github.com/thomasjpfan/skconfig',
    packages=find_packages(include=['skconfig']),
    install_requires=install_requires,
    include_package_data=True,
    python_requires='>=3.5',
    zip_safe=False,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    extras_require={
        'dev': dev_requires,
    })
