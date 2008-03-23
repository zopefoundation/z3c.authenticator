##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.authentication.password import PlainTextPasswordManager
from zope.app.testing import setup

###############################################################################
#
# setup helper
#
###############################################################################

def setUpPasswordManager():
    zope.component.provideUtility(PlainTextPasswordManager(), 
        IPasswordManager, "Plain Text")


###############################################################################
#
# placeful setup/teardown
#
###############################################################################

def siteSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site


def siteTearDown(test):
    setup.placefulTearDown()
