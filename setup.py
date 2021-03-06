#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

from simpleservice import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    install_requires=('WebOb>=1.2.3',
                      'Paste>=1.7.4', 'PasteDeploy>=1.5.0',
                      'Routes>2.3.1',
                      'sqlalchemy>=1.0.11',
                      'kombu>=3.0.25',
                      'six>=1.9.0',
                      'requests>=2.11.1',
                      'simpleutil>=1.0',
                      'simpleutil<1.1',
                      ),
    name='simpleservice',
    version=__version__,
    description='a simple copy of service from openstack',
    long_description=long_description,
    url='http://github.com/lolizeppelin/simpleservice',
    author='Lolizeppelin',
    author_email='lolizeppelin@gmail.com',
    maintainer='Lolizeppelin',
    maintainer_email='lolizeppelin@gmail.com',
    keywords=['simpleservice'],
    license='MIT',
    packages=find_packages(include=['simpleservice*']),
    # tests_require=['pytest>=2.5.0'],
    # cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
