##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup
"""
import os

from setuptools import find_packages
from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name='z3c.authenticator',
    version='2.0',
    author="Roger Ineichen and the Zope Community",
    author_email="zope-dev@zope.dev",
    description="IAuthentication implementation for for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n.. contents::\n\n' +
        read('src', 'z3c', 'authenticator', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'authenticator', 'group.txt')
        + '\n\n' +
        read('src', 'z3c', 'authenticator', 'vocabulary.txt')
        + '\n\n' +
        read('CHANGES.txt')
    ),
    license="ZPL 2.1",
    keywords="zope3 z3c authentication auth group",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    url='https://github.com/zopefoundation/z3c.authenticator',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    python_requires='>=3.7',
    extras_require=dict(
        test=[
            'z3c.testing >= 1.0.0a3',
            'zope.testing',
        ],
        configurator=[
            'z3c.configurator',
        ],
    ),
    install_requires=[
        'setuptools',
        'z3c.contents',
        'z3c.form',
        'z3c.formui',
        'z3c.template',
        'zope.authentication',
        'zope.component',
        'zope.container',
        'zope.deprecation',
        'zope.dublincore',
        'zope.event',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.password',
        'zope.principalregistry',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.session',
        'zope.site',
        'zope.traversing',
    ],
    test_suite='z3c.authenticator.tests.test_suite',
    zip_safe=False,
)
