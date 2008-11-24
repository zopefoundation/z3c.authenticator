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

import zope.interface

from z3c.authenticator import interfaces


# principal events
class AuthenticatedPrincipalCreated(object):
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = AuthenticatedPrincipalCreated('authentication', 'principal',
    ...     'request')
    >>> verifyObject(interfaces.IAuthenticatedPrincipalCreated, event)
    True
    """

    zope.interface.implements(interfaces.IAuthenticatedPrincipalCreated)

    def __init__(self, authentication, principal, request):
        self.authentication = authentication
        self.principal = principal
        self.request = request


class UnauthenticatedPrincipalCreated(object):
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = UnauthenticatedPrincipalCreated('authentication', 'principal',
    ...     'request')
    >>> verifyObject(interfaces.IUnauthenticatedPrincipalCreated, event)
    True
    """

    zope.interface.implements(interfaces.IUnauthenticatedPrincipalCreated)

    def __init__(self, authentication, principal):
        self.authentication = authentication
        self.principal = principal


class FoundPrincipalCreated(object):
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = FoundPrincipalCreated('authentication', 'principal')
    >>> verifyObject(interfaces.IFoundPrincipalCreated, event)
    True
    """

    zope.interface.implements(interfaces.IFoundPrincipalCreated)

    def __init__(self, authentication, principal):
        self.authentication = authentication
        self.principal = principal


# group events
class GroupAdded(object):
    """Group added event

    >>> from zope.interface.verify import verifyObject
    >>> event = GroupAdded(u'group')
    >>> verifyObject(IGroupAdded, event)
    True
    """

    zope.interface.implements(interfaces.IGroupAdded)

    def __init__(self, group):
        self.group = group

    def __repr__(self):
        return "<GroupAdded %r>" % self.group.__name__


class AbstractUsersChanged(object):

    def __init__(self, principal_ids, group_id):
        self.principal_ids = principal_ids
        self.group_id = group_id

    def __repr__(self):
        return "<%s %r %r>" % (
            self.__class__.__name__, sorted(self.principal_ids), self.group_id)


class PrincipalsAddedToGroup(AbstractUsersChanged):
    zope.interface.implements(interfaces.IPrincipalsAddedToGroup)


class PrincipalsRemovedFromGroup(AbstractUsersChanged):
    zope.interface.implements(interfaces.IPrincipalsRemovedFromGroup)
