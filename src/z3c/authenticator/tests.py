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
import doctest
import re
import unittest

import zope.site.testing
import zope.password.testing
import zope.component.testing
from z3c.testing import BaseTestIContainer
from z3c.testing import InterfaceBaseTest
from zope.testing.renormalizing import RENormalizing

from z3c.authenticator import authentication
from z3c.authenticator import credential
from z3c.authenticator import group
from z3c.authenticator import interfaces
from z3c.authenticator import principal
from z3c.authenticator import testing
from z3c.authenticator import user


class AuthenticatorTest(BaseTestIContainer):

    def getTestInterface(self):
        return interfaces.IAuthenticator

    def getTestClass(self):
        return authentication.Authenticator


class UserContainerTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IUserContainer

    def getTestClass(self):
        return user.UserContainer


class UserTest(InterfaceBaseTest):

    def setUp(self):
        testing.setUpPasswordManager()

    def getTestInterface(self):
        return interfaces.IUser

    def getTestClass(self):
        return user.User

    def getTestPos(self):
        return (u'login', u'password', u'Title')


class AuthenticatedPrincipalTest(InterfaceBaseTest):

    def setUp(self):
        testing.setUpPasswordManager()

    def getTestInterface(self):
        return interfaces.IAuthenticatedPrincipal

    def getTestClass(self):
        return principal.AuthenticatedPrincipal

    def makeTestObject(self):
        usr =  user.User(u'login', u'password', u'Title')
        return principal.AuthenticatedPrincipal(usr)


class FoundPrincipalTest(InterfaceBaseTest):

    def setUp(self):
        testing.setUpPasswordManager()

    def getTestInterface(self):
        return interfaces.IFoundPrincipal

    def getTestClass(self):
        return principal.FoundPrincipal

    def makeTestObject(self):
        usr =  user.User(u'login', u'password', u'Title')
        return principal.FoundPrincipal(usr)


class GroupContainerTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IGroupContainer

    def getTestClass(self):
        return group.GroupContainer


class GroupTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IGroup

    def getTestClass(self):
        return group.Group


class SessionCredentialsTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISessionCredentials

    def getTestClass(self):
        return credential.SessionCredentials

    def getTestPos(self):
        return (u'login', u'password')


class SessionCredentialsPluginTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ICredentialsPlugin

    def getTestClass(self):
        return credential.SessionCredentialsPlugin


class SessionCredentialsPluginFormTest(InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IBrowserFormChallenger

    def getTestClass(self):
        return credential.SessionCredentialsPlugin

def placefulSetUp(test):
    test.globs['rootFolder'] = zope.site.testing.siteSetUp(True)
    zope.traversing.testing.setUp()
    zope.password.testing.setUpPasswordManagers()

def placefulTearDown(test):
    zope.site.testing.siteTearDown()

def test_suite():
    checker = RENormalizing((
            (re.compile("u'(.*?)'"), "'\\1'"),
            (re.compile("z3c.authenticator.group.GroupCycle"), "GroupCycle"),
            ))
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', checker=checker,
            setUp=testing.placefulSetUp, tearDown=testing.placefulTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite(
                'group.txt', checker=checker,
                setUp=testing.placefulSetUp, tearDown=testing.placefulTearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
                'z3c.authenticator.credential', checker=checker,
                setUp=testing.placefulSetUp, tearDown=testing.placefulTearDown),
        doctest.DocTestSuite(
                'z3c.authenticator.group',
                setUp=testing.placefulSetUp,
                tearDown=testing.placefulTearDown),
        doctest.DocFileSuite(
                'vocabulary.txt', checker=checker,
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown),
        unittest.makeSuite(AuthenticatorTest),
        unittest.makeSuite(UserContainerTest),
        unittest.makeSuite(UserTest),
        unittest.makeSuite(AuthenticatedPrincipalTest),
        unittest.makeSuite(FoundPrincipalTest),
        unittest.makeSuite(GroupContainerTest),
        unittest.makeSuite(GroupTest),
        unittest.makeSuite(SessionCredentialsTest),
        unittest.makeSuite(SessionCredentialsPluginTest),
        unittest.makeSuite(SessionCredentialsPluginFormTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
