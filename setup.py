#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

from simpleutil import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    # oslo_cfg 要求 netaddr!=0.7.16,>=0.7.12 # BSD
    # kombu>=3.0.25否则timeout参数有问题
    install_requires=('netaddr>=0.7.5', 'eventlet>=0.15.2', 'routes>=1.12.3'  'routes<2.0',
                      'WebOb'>='1.2.3', 'Paste', 'PasteDeploy>=1.5.0', 'kombu>=3.0.25',
                      'six>=1.9.0', 'simpleutil>=1.0'),
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
    packages=['simpleservice'],
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
    ]
)
