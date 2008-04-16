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
    version='0.5.1dev',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "IAuthentication implementation for for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c json rpc tree",
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
    url = 'http://cheeseshop.python.org/pypi/z3c.authenticator',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.template',
            'z3c.testing',
            'zope.app.publication',
            'zope.app.publisher',
            'zope.app.security',
            'zope.app.testing',
            'zope.configuration',
            'zope.pagetemplate',
            'zope.publisher',
            'zope.testbrowser',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.i18n',
        'z3c.template',
        'z3c.contents',
        'z3c.table',
        'z3c.form',
        'z3c.formui',
        'zope.app.component',
        'zope.app.container',
        'zope.component',
        'zope.interface',
        'zope.proxy',
        'zope.publisher',
        'zope.security',
        'zope.traversing',
        'zope.viewlet',

        ],
    zip_safe = False,
)
