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
"""Testing Support
"""
import zope.component
import zope.interface
import zope.traversing
from zope.password.interfaces import IPasswordManager
from zope.password.password import PlainTextPasswordManager
from zope.publisher.interfaces import IRequest
from zope.session.http import CookieClientIdManager
from zope.session.interfaces import IClientId
from zope.session.interfaces import IClientIdManager
from zope.session.interfaces import ISession
from zope.session.interfaces import ISessionDataContainer
from zope.session.session import RAMSessionDataContainer
from zope.session.session import Session


###############################################################################
#
# setup helper
#
###############################################################################


def setUpPasswordManager():
    zope.component.provideUtility(PlainTextPasswordManager(),
                                  IPasswordManager, "Plain Text")


@zope.interface.implementer(IClientId)
class TestClientId:
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
    site = zope.site.testing.siteSetUp(site=True)
    test.globs['rootFolder'] = site
    zope.traversing.testing.setUp()
    setUpPasswordManager()


def placefulTearDown(test):
    zope.site.testing.siteTearDown()
