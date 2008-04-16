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
import zope.interface
from zope.publisher.interfaces import IRequest
from zope.app.testing import setup

from zope.session.interfaces import IClientId
from zope.session.interfaces import IClientIdManager
from zope.session.interfaces import ISession
from zope.session.interfaces import ISessionDataContainer
from zope.session.session import Session
from zope.session.session import RAMSessionDataContainer
from zope.session.http import CookieClientIdManager

from z3c.authenticator.interfaces import IPasswordManager
from z3c.authenticator.password import PlainTextPasswordManager

###############################################################################
#
# setup helper
#
###############################################################################

def setUpPasswordManager():
    zope.component.provideUtility(PlainTextPasswordManager(), 
        IPasswordManager, "Plain Text")


class TestClientId(object):
    zope.interface.implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'


def sessionSetUp(session_data_container_class=RAMSessionDataContainer):
    zope.component.provideAdapter(TestClientId, (IRequest,), IClientId)
    zope.component.provideAdapter(Session, (IRequest,), ISession)
    zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)
    sdc = session_data_container_class()
    zope.component.provideUtility(sdc, ISessionDataContainer, name='')


###############################################################################
#
# placeful setup/teardown
#
###############################################################################

def placefulSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site
    setUpPasswordManager()


def placefulTearDown(test):
    setup.placefulTearDown()
