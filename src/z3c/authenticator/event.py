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
"""Events
"""
import zope.interface

from z3c.authenticator import interfaces


# principal events
@zope.interface.implementer(interfaces.IAuthenticatedPrincipalCreated)
class AuthenticatedPrincipalCreated:
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = AuthenticatedPrincipalCreated('authentication', 'principal',
    ...     'request')
    >>> verifyObject(interfaces.IAuthenticatedPrincipalCreated, event)
    True
    """

    def __init__(self, authentication, principal, request):
        self.authentication = authentication
        self.principal = principal
        self.request = request


@zope.interface.implementer(interfaces.IUnauthenticatedPrincipalCreated)
class UnauthenticatedPrincipalCreated:
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = UnauthenticatedPrincipalCreated('authentication', 'principal')
    >>> verifyObject(interfaces.IUnauthenticatedPrincipalCreated, event)
    True
    """

    def __init__(self, authentication, principal):
        self.authentication = authentication
        self.principal = principal


@zope.interface.implementer(interfaces.IFoundPrincipalCreated)
class FoundPrincipalCreated:
    """
    >>> from zope.interface.verify import verifyObject
    >>> event = FoundPrincipalCreated('authentication', 'principal')
    >>> verifyObject(interfaces.IFoundPrincipalCreated, event)
    True
    """

    def __init__(self, authentication, principal):
        self.authentication = authentication
        self.principal = principal


# group events
@zope.interface.implementer(interfaces.IGroupAdded)
class GroupAdded:
    """Group added event

    >>> from zope.interface.verify import verifyObject
    >>> event = GroupAdded(u'group')
    >>> verifyObject(interfaces.IGroupAdded, event)
    True
    """

    def __init__(self, group):
        self.group = group

    def __repr__(self):
        return "<GroupAdded %r>" % self.group.__name__


class AbstractUsersChanged:

    def __init__(self, principal_ids, group_id):
        self.principal_ids = principal_ids
        self.group_id = group_id

    def __repr__(self):
        return "<{} {!r} {!r}>".format(
            self.__class__.__name__, sorted(self.principal_ids), self.group_id)


@zope.interface.implementer(interfaces.IPrincipalsAddedToGroup)
class PrincipalsAddedToGroup(AbstractUsersChanged):
    pass


@zope.interface.implementer(interfaces.IPrincipalsRemovedFromGroup)
class PrincipalsRemovedFromGroup(AbstractUsersChanged):
    pass
