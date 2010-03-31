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

$Id:$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='z3c.authenticator',
    version='0.6.3',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "IAuthentication implementation for for Zope3",
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
    license = "ZPL 2.1",
    keywords = "zope3 z3c authentication auth group",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/z3c.authenticator',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.testing',
            'zope.app.testing',
            'zope.publisher',
            'zope.session',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.configurator',
        'z3c.contents',
        'z3c.form',
        'z3c.formui',
        'z3c.i18n',
        'z3c.template',
        'zope.app.component',
        'zope.app.container',
        'zope.app.generations',
        'zope.app.security',
        'zope.component',
        'zope.deprecation',
        'zope.dublincore',
        'zope.event',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.session',
        'zope.traversing',
        'zope.deferredimport',
        ],
    zip_safe = False,
)
